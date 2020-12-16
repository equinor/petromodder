import pandas as pd
import xtgeo
from pathlib import Path
import os
import xml.etree.ElementTree as ET
import warnings
import re
from shapely.geometry import Point, Polygon,LineString
import numpy as np
import datetime
import xtgeo

tested_version = ["2017.1", "2019.1"]


class PetroMod:
    def __init__(self, path_in):
        self.path = Path(path_in)
        self.facies_maps = self.path / "in//ts1//bl1//faci_m//cont.pmt"
        self.depth_maps = self.path / "in//ts1//bl1//dpth_m//cont.pmt"
        self.heatflow_maps = self.path / "in//hf_m//cont.pmt"
        self.pwd_maps = self.path / "in//pdp_m//cont.pmt"
        self.maps = self.path / "in//ts1//bl1//"  # for subsheat building

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        """Validate PetroMod model
        
        Arguments:
            path {pathlib path} -- path to PetroMod model
        
        Raises:
            Exception: Invalid PetroMod model
        """
        check = 0
        for name in os.listdir(path):
            if "in" == name:
                check += 1
            elif "def" == name:
                check += 1
            else:
                pass
        if check != 2:
            raise Exception("Invalid PetroMod directory")
        else:
            print("Valid PetroMod model")
        self.check_sublayer(path / "in//ts1//bl1//subl.pmt")
        self._path = path
        self.ndim
        if self.version not in tested_version:
            raise Exception("Model version not supported")
        return

    @property
    def lithology(self):
        """Parse PetroMod lithology xml
        
        Returns:
            dict -- Lithology properties by lithology code
        """
        tree = ET.parse(self.path.parents[1] / "geo//Lithologies.xml")
        root = tree.getroot()
        meta = self.litho_meta(root)
        litho = self.litho_lith(root, meta)
        return litho

    def litho_meta(self, xml_root):
        for x in xml_root.findall("Meta"):
            m = {}
            for y in x.findall("MetaParameterGroup"):
                for i in y.findall("Name"):
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
                    if self.version == "2017.1":
                        for u in i.findall("PetroModId"):
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
                    elif self.version == "2019.1":
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

    @property
    def lookup_table(self):
        layerdef = self.read_pmt(self.path / "in//layerdef.pmt")
        horizongeom = self.read_pmt(self.path / "in//ts1//bl1//horizongeom.pmt")
        horizongeom = horizongeom[["HorizonID", "HorizonGeomID", "FaciesMapID"]]
        df = layerdef.merge(horizongeom, on="HorizonID")
        df = df[df.HorizonAge != 99999.0]
        return df

    def check_sublayer(self, filepath):
        """Check if the model contains different properties for sublayers
        """
        df = self.read_pmt(filepath)
        df = df.groupby("LayerID").FaciesMapID.nunique() > 1
        a = df[df].index.tolist()
        if len(a) != 0:
            warnings.warn(
                "Sublayers not supported. Properties from the topmost layer will be applied to all sublayers"
            )
        else:
            pass
        return

    @property
    def ndim(self):
        """Check model dimensions"""
        path = str(self.path)
        if "pm3d" in path:
            ndim = 3
        elif "pm2d" in path:
            ndim = 2
        elif "pm1d" in path:
            ndim = 1
        else:
            raise Exception("Invalid PetroMod directory")
        return ndim

    def read_pmt(self, fullpath):
        """Parse PetroMod PMT file"""
        with (open(fullpath)) as f:
            for i, line in enumerate(f):
                if line.startswith("Key"):
                    ind = i
                elif line.startswith("Data"):
                    data = i - ind - 1
                    break
        if ind == None or data == None:
            raise Exception("Invalid PMT file")
        df = pd.read_table(fullpath, delimiter="|", header=ind)
        df = df.rename(columns=lambda x: x.strip())
        df = df.iloc[(data):]
        df = df.reset_index(drop=True)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.apply(pd.to_numeric, errors="ignore")
        return df

    def write_pmt(self, PM_data_type, df, col_num, headers):
        """[summary]
        
        Arguments:
            type {str} -- PM data table type for meta header
            df {DataFrame} -- dats to export
            col_num {int} -- Number of columns in the data table
            headers {list of list} -- List of headers. Last one is format header
        
        Raises:
            Exception: Input col num and header col number mismatch
            Exception: Length of header length mismatch
        
        Returns:
            output {str} -- markdown table in PM format
        
 
        """
        # Make meta header
        version = "c " + PM_data_type + " [PetroMod " + self.version + "]"
        meta = """c\n{vars}\nc\n""".format(
            length="multi-line", ordinal="second", vars=version
        )
        # Error check col_numbers vs header
        for i in headers:
            if len(i) != col_num:
                raise Exception("Headers and column numbers mismatch")
        # Fix df cell length
        while df.shape[1] > col_num:
            df = df.drop(df.columns[-1], axis=1)
        # max len of all cell and header by column in df
        measurer = np.vectorize(len)
        df_header_len = list(map(len, df.columns))
        max_len_df = measurer(df.values.astype(str)).max(axis=0)
        df_len = list(map(max, max_len_df, df_header_len))
        # PM header and format header length
        head = pd.DataFrame(headers)
        max_header = measurer(head.values.astype(str)).max(axis=0)
        # Make sure df header string length is same as PM header length
        col = list(df.columns)
        for i in range(len(df_len)):
            if df_len[i] > max_header[i]:
                pass
            elif df_len[i] < max_header[i]:
                col[i] = col[i].ljust(max_header[i])
        df.columns = col
        # df to markdown
        a = df.to_markdown()
        # get header from markdon
        b = a.splitlines()[0]
        # Count string len between pipes in header
        def find_all(a_str, sub):
            start = 0
            while True:
                start = a_str.find(sub, start)
                if start == -1:
                    return
                yield start
                start += len(sub)  # use start += 1 to find overlapping matches

        # Index of pipes
        ind = np.array(list(find_all(b, "|")))
        # Length of string in header between pipes
        diff = np.diff(ind) - 1
        diff = diff[1:]
        # Strip header in markdown
        c = a.split("\n", 2)[-1]
        # Loop multiline string to strip first col in markdown
        stripped = ""
        for x in iter(c.splitlines()):
            x_ = x[ind[1] + 2 :]
            stripped = stripped + x_ + "\n"

        def add_header_prop(list_header, size_header):
            out = ""
            for ind, x in enumerate(list_header):
                if len(x) > size_header[ind]:
                    raise Exception("Format error")
                elif len(x) < size_header[ind]:
                    if ind > 0:
                        string = x.center(size_header[ind])
                    else:
                        string = x.ljust(size_header[ind] - 1)
                else:
                    string = x
                string = string + "|"
                out = out + string
            return out

        header = ""
        for i in headers[:-1]:
            h = add_header_prop(i, diff)
            header = header + h + "\n"
        format_header = add_header_prop(headers[-1], diff) + "\n"
        div_1 = "Stop"
        div_1 = div_1.ljust(len(format_header), "-") + "\n"
        div_2 = "c"
        div_2 = div_2.ljust(len(format_header), "-") + "\n"
        output = meta + header + div_1 + format_header + div_2 + stripped
        return output

    @property
    def version(self):
        version = []
        fullpath = self.path / "in//aoigrid.pmt"
        while len(version) == 0:
            with (open(fullpath)) as f:
                for line in f:
                    if line.startswith("c AOI and Grid"):
                        version.append(line)
                        break
        version = str(version[0])
        startind = version.find("PetroMod ")
        version = version[startind + 9 : -2]
        return version

    @property
    def grid_size(self):
        aoi_table = self.read_pmt(self.path / "in//aoi_m//cont.pmt")
        aoi_file_name = aoi_table.ID[0]
        aoi_file_name = str(aoi_file_name)
        aoi_file_name = aoi_file_name + ".pmd"
        aoi_map_path = self.path / "in//aoi_m//" / aoi_file_name
        aoi = xtgeo.surface_from_file(aoi_map_path, fformat="petromod")
        if aoi.xinc != aoi.yinc:
            warnings.warn("Different x and y intervals is not supported")
        return {"xinc": aoi.xinc, "yinc": aoi.yinc}

    @property
    def heatflow_age(self):
        try:
            df = self.read_pmt(self.path / "in//heat.pmt")
            df = df["Age"].values
            df = df.astype(int)
        except:
            raise Exception("No heatflow table in PM. Open PM and create table first")
        return df

    def add_heatflow_maps(self, map_dict, folder_name=None):
        """[summary]

        Args:
            map_dict (dict): Dictionary containing: Keys: Age of map in string. Value: HF map in xtgeo surface object
            folder_name (str, optional): Name of folder of maps in PetroMod. Defaults to None.
        """
        # Check existing HF map index
        try:
            df = self.heatflow_maps_index
            max_id = df["ID"].max() + 1
        except:  # create new
            if os.path.isdir(self.path / "in//hf_m") == False:
                warnings.warn(
                    "Heat flow maps folder does not exist. Creating an empty folder..."
                )
                os.mkdir(self.path / "in//hf_m")
            else:
                warnings.warm("No heatflow map index file found. Creating cont.pmt..")
            df = pd.DataFrame(columns=["Key", "ID", "Level", "NameInTree"])
            max_id = 1
        # Add new folder to the index
        if isinstance(folder_name, str):
            df = df.append(
                {"Key": "Data", "ID": max_id, "Level": 1, "NameInTree": folder_name},
                ignore_index=True,
            )
            max_id = max_id + 1
        elif isinstance(folder_name, type(None)):
            pass
        else:
            pass
        # Export HF map as PMD and update hf map index
        for k, v in map_dict.items():
            f = "in//hf_m/" + str(max_id) + ".pmd"
            filepath = self.path / f
            filepath = str(filepath.resolve())
            v.to_file(filepath, fformat="petromod", pmd_dataunits=(15, 44))
            map_dict.update({k: max_id})
            # construct HF maps index table
            nameintree = k + "Ma"
            df = df.append(
                {"Key": "Data", "ID": max_id, "Level": 2, "NameInTree": nameintree},
                ignore_index=True,
            )
            max_id = max_id + 1
        headers = [
            ["Head", "ID", "Level", "Name"],
            ["Key", "ID", "Level", "NameInTree"],
            ["Format", "%4d", "%2d", "%s"],
        ]
        # update hf map index
        output = self.write_pmt("Standard Content", df, 4, headers)
        with open(self.path / "in//hf_m//cont.pmt", "w+") as f:
            f.write(output)
        return map_dict

    def update_heatflow_model(self, map_dict):
        age = np.empty(0)
        maps_file_id = np.empty(0)
        for k, v in map_dict.items():
            a = float(k)
            age = np.append(age, a)
            maps_file_id = np.append(maps_file_id, v)
        size = age.size
        key = np.full(size, "Data")
        mode = np.ones(size)
        value = np.full(size, 99999.0000)  # 99999.0000 in PM means use map for HF
        data = {
            "Key": key,
            "Age": age,
            "Mode": mode,
            "Value": value,
            "Map": maps_file_id,
        }
        df = pd.DataFrame.from_dict(data)

        headers = [
            ["Head", "Age from", "Mode", "Value", "Map"],
            ["Head", "[Ma]", "", "[mW/m^2]", ""],
            ["Key", "Age", "Mode", "Value", "Map"],
            ["Format", "%6.4f", "%d", "%6.4f", "%d"],
        ]
        output = self.write_pmt("Heat Flow", df, 5, headers)
        with open(self.path / "in//heat.pmt", "w+") as f:
            f.write(output)
        return

    def add_paleo_water_depth_maps(
        self, map_dict, folder_name=None, update_model=False
    ):
        """[summary]

        Args:
            map_dict (dict): Dictionary containing: Keys: Age of map in string. Value: PWD map in xtgeo surface object
            folder_name (str, optional): Name of folder of maps in PetroMod. Defaults to None.
            update_model (bool, optional): Set PWD maps to active in PetroMod. Defaults to False.
        """
        # Check existing HF map index
        try:
            df = self.pwd_maps_index
            max_id = df["ID"].max() + 1
        except:  # create new
            if os.path.isdir(self.path / "in//pdp_m") == False:
                warnings.warn(
                    "Paleo Water Depth maps folder does not exist. Creating an empty folder..."
                )
                os.mkdir(self.path / "in//pdp_m")
            else:
                warnings.warm(
                    "No Paleo Water Depth map index file found. Creating cont.pmt.."
                )
            df = pd.DataFrame(columns=["Key", "ID", "Level", "NameInTree"])
            max_id = 1
        # Add new folder to the index
        if isinstance(folder_name, str):
            df = df.append(
                {"Key": "Data", "ID": max_id, "Level": 1, "NameInTree": folder_name},
                ignore_index=True,
            )
            max_id = max_id + 1
        elif isinstance(folder_name, type(None)):
            pass
        else:
            pass
        # Export HF map as PMD and update hf map index
        for k, v in map_dict.items():
            f = "in//pdp_m/" + str(max_id) + ".pmd"
            filepath = self.path / f
            filepath = str(filepath.resolve())
            v.to_file(filepath, fformat="petromod", pmd_dataunits=(15, 10))
            map_dict.update({k: max_id})
            # construct HF maps index table
            nameintree = k + "Ma"
            df = df.append(
                {"Key": "Data", "ID": max_id, "Level": 2, "NameInTree": nameintree},
                ignore_index=True,
            )
            max_id = max_id + 1
        headers = [
            ["Head", "ID", "Level", "Name"],
            ["Key", "ID", "Level", "NameInTree"],
            ["Format", "%4d", "%2d", "%s"],
        ]
        # update hf map index
        output = self.write_pmt("Standard Content", df, 4, headers)
        with open(self.path / "in//pdp_m//cont.pmt", "w+") as f:
            f.write(output)
        return map_dict

    def update_paleo_water_depth_model(self, map_dict):
        age = np.empty(0)
        maps_file_id = np.empty(0)
        for k, v in map_dict.items():
            a = float(k)
            age = np.append(age, a)
            maps_file_id = np.append(maps_file_id, v)
        size = age.size
        key = np.full(size, "Data")
        mode = np.ones(size)
        ref = np.zeros(size)
        layer = np.ones(size) * -1
        value = np.full(size, 99999.0000)  # 99999.0000 in PM means use map for HF
        data = {
            "Key": key,
            "AgeFrom": age,
            "Reference": ref,
            "Layer": layer,
            "Mode": mode,
            "Value": value,
            "Map": maps_file_id,
        }
        df = pd.DataFrame.from_dict(data)

        headers = [
            ["Head", "Age from", "Reference", "Layer", "Mode", "Depth", "Depth Map",],
            ["Head", "[Ma]", "", "", "", "[m]", ""],
            ["Key", "AgeFrom", "Reference", "Layer", "Mode", "Value", "Map"],
            ["Format", "%6.4f", "%d", "%d", "%d", "%6.4f", "%d"],
        ]
        output = self.write_pmt("Water Depth / Paleo Depth", df, 7, headers)
        with open(self.path / "in//palg.pmt", "w+") as f:
            f.write(output)
        return

    @property
    def pwd_age(self):
        try:
            df = self.read_pmt(self.path / "in//palg.pmt")
            df = df["AgeFrom"].values
            df = df.astype(int)
        except:
            raise Exception(
                "No Paleo-water depth table in PM. Open PM and create table first"
            )
        return df

    @property
    def facies_table(self):
        try:
            df = self.read_pmt(self.path / "in//uni3.pmt")
        except:
            raise Exception("No facies defined in PM. Open PM and create table first")
        return df

    @property
    def heatflow_maps_index(self):
        try:
            df = self.read_pmt(self.path / "in//hf_m/cont.pmt")
            while df.shape[1] > 4:
                df = df.drop(df.columns[-1], axis=1)
        except:
            raise Exception("No heatflow maps in PM")
        return df

    @property
    def pwd_maps_index(self):
        try:
            df = self.read_pmt(self.path / "in//pdp_m/cont.pmt")
            while df.shape[1] > 4:
                df = df.drop(df.columns[-1], axis=1)
        except:
            raise Exception("No Paleo-water depth maps in PM")
        return df

    @property
    def block_boundary(self):
        exist = False
        filepath = self.path.parents[1] / "cult"
        for f in os.listdir(filepath):
            if f == "blockbound.pmt":
                exist = True
                break
        if exist == True:
            polygons = self.make_polygons("blockbound.pmt")
        else:
            polygons = None
            warnings.warn("No crossline in the project")
        return polygons

    @property
    def polygons(self):
        exist = False
        filepath = self.path.parents[1] / "cult"
        for f in os.listdir(filepath):
            if f == "line.pmt":
                exist = True
                break
        if exist == True:
            polygons = self.make_polygons("line.pmt")
        else:
            polygons = None
            warnings.warn("No polygon in the project")
        return polygons

    @property
    def crossline(self):
        exist = False
        filepath = self.path.parents[1] / "cult"
        for f in os.listdir(filepath):
            if f == "crossline.pmt":
                exist = True
                break
        if exist == True:
            polygons = self.make_polygons("crossline.pmt")
        else:
            polygons = None
            warnings.warn("No crossline in the project")
        return polygons

    def make_polygons(self, item):
        """Make Shapely object from PetroMod polygons/lines
        
        Arguments:
            item {path} -- PetroMod PMT file containing polygons/lines
        
        Returns:
            dict -- key: polygon name, value: Shapely object
        """
        poly_all = {}
        line_all={}
        filepath = self.path.parents[1] / "cult"
        fpath = filepath / item
        df = self.read_pmt(fpath)
        poly_name = pd.unique(df["Name"])
        poly_id = pd.unique(df["GID"]).astype(int)
        for ind, i in enumerate(poly_id):
            df_filtered = df[df["GID"] == i]
            first = df_filtered.iloc[0]
            last = df_filtered.iloc[-1]
            if first.equals(last) == True:
                xx = df_filtered["X"]
                yy = df_filtered["Y"]
                ls_pt = np.dstack((xx, yy))[0]
                Point_ls_pt = []
                for i in ls_pt:
                    x = Point(i)
                    Point_ls_pt.append(x)
                coords = [p.coords[:][0] for p in Point_ls_pt]
                poly = Polygon(coords)
                poly_all.update({poly_name[ind]: poly})
            else:
                xx = df_filtered["X"]
                yy = df_filtered["Y"]
                ls_pt = np.dstack((xx, yy))[0]
                Point_ls_pt = []
                for i in ls_pt:
                    x = Point(i)
                    Point_ls_pt.append(x)
                coords = [p.coords[:][0] for p in Point_ls_pt]
                poly = LineString(coords)
                line_all.update({poly_name[ind]: poly})
        line_poly = {"polygon":poly_all, "lines":line_all}
        return line_poly
