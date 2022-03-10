import xml.etree.ElementTree as ET


class Lithology:
    """Lithology data of the project
    """

    def __init__(self, project_path):
        self.__lithology_path = project_path / "geo//Lithologies.xml"

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
            # log warning
            litho = False
        return litho

    def _litho_meta(self, xml_root):
        metadata = xml_root.find("Meta")
        lithologies_meta = {}
        for meta_gp in metadata.findall("MetaParameterGroup"):
            meta_gp_name = meta_gp.find("Name").text
            meta_gp_id = meta_gp.find("Id").text
            name = []
            key = []
            for param in meta_gp.findall("MetaParameter"):
                param_name = param.find("Name").text
                name.append(param_name)
                param_val = param.find("Id").text
                key.append(param_val)
            temp = dict(zip(key, name))
            lithologies_meta.update(
                {meta_gp_id: {'parameter_group': meta_gp_name, 'parameters': temp}})
        return lithologies_meta

    def _litho_lith(self, xml_root, meta):
        # return a flat lithology structure
        lith = {}
        for lith_gp in xml_root.findall("LithologyGroup"):
            for lithologies in lith_gp.findall("LithologyGroup"):
                lith_id = self._parse_lithology_gp(lithologies, meta)
                lith.update(lith_id)
        return lith

    def _parse_lithology_gp(self, lith, meta):
        # parse one lith_gp
        lithologies = {}
        for lithology in lith.findall("Lithology"):
            lithology_parsed = self._parse_lithology(lithology, meta)
            lithologies.update(lithology_parsed)
        return lithologies

    def _parse_lithology(self, lithology, meta):
        # parse one lith
        rock_id = lithology.find("Id").text
        given_name = lithology.find('Name').text
        allgp = {'name': given_name}
        for param_gp in lithology.findall("ParameterGroup"):
            param_gp_parsed = self._parse_param_gp(param_gp, meta)
            allgp.update(param_gp_parsed)
        return {rock_id: allgp}

    def _parse_param_gp(self, param_gp, meta):
        # parse one parameters group
        gp_id = param_gp.find('MetaParameterGroupId').text
        param_gp_name = meta[gp_id]['parameter_group']
        name = []
        value = []
        for param in param_gp.findall("Parameter"):
            param_id = meta[gp_id]['parameters'][param.find(
                "MetaParameterId").text]
            name.append(param_id)
            paramval = param.find("Value").text
            value.append(paramval)
        temp = dict(zip(name, value))
        return {param_gp_name: temp}
