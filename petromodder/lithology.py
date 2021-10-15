import xml.etree.ElementTree as ET

class Lithology:
    def __init__(self,project_path):
        self.__lithology_path__ = project_path/ "geo//Lithologies.xml"
    @property
    def lithology(self):
        """Parse PetroMod lithology xml
        
        Returns:
            dict -- Lithology properties by lithology code
        """

        if self.__lithology_path__.exists():
            tree = ET.parse(self.__lithology_path__)
            root = tree.getroot()
            meta = self.litho_meta(root)
            litho = self.litho_lith(root, meta)
        else:
            #log warning
            litho=False
        return litho

    def litho_meta(self, xml_root):
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

    def litho_lith(self, xml_root, meta):
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
