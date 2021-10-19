import xml.etree.ElementTree as ET

class Lithology:
    """Lithology data of the project
    """
    def __init__(self,project_path):
        self.__lithology_path = project_path/ "geo//Lithologies.xml"
    @property
    def lithology(self):
        """Lithology database of the project

        Returns
        -------
        dict
            Lithology database of the project
        """
        if self.__lithology_path.exists():
            tree = ET.parse(self.__lithology_path)
            root = tree.getroot()
            meta = self._litho_meta(root)
            litho = self._litho_lith(root, meta)
        else:
            #log warning
            litho=False
        return litho

    def _litho_meta(self, xml_root):
        for x in xml_root.findall("Meta"):
            m = {}
            for y in x.findall("MetaParameterGroup"):
                for j in y.findall("Name"):
                    # topname = i.text
                    name = []
                    value = []
                    for i in y.findall("MetaParameter"):
                        for z in i.findall("Name"):
                            # print(z.text)
                            item = z.text
                            name.append(item)
                        for q in i.findall("Id"):
                            # print(q.text)
                            val = q.text
                            value.append(val)
                    temp = dict(zip(value, name))
                    # print(temp)
                    temp.update(temp)
                    # e = {topname: temp}
                    m.update(temp)
        return m

    def _litho_lith(self, xml_root, meta):
        lith = {}
        for x in xml_root.findall("LithologyGroup"):
            for y in x.findall("LithologyGroup"):
                for i in y.findall("Lithology"):
                    for u in i.findall("Id"):
                        rock_name = u.text
                        allgp = {}
                        for u in i.findall("ParameterGroup"):
                            for uu in u.findall("MetaParameterGroupId"):
                                # paramGP = uu.text
                                name = []
                                value = []
                                for uu in u.findall("Parameter"):
                                    for uuu in uu.findall("MetaParameterId"):
                                        paramid = meta[uuu.text]
                                        name.append(paramid)
                                    for uuu in uu.findall("Value"):
                                        paramval = uuu.text
                                        value.append(paramval)
                                temp = dict(zip(name, value))
                                # paramGP = {paramGP: temp}
                                allgp.update(temp)
                        lith_id = {rock_name: allgp}
                        lith.update(lith_id)
        return lith
