
from .utils import Utils
from .base_model import Base_Model
from .logging import logger
import os
import xtgeo
import numpy as np
import pandas as pd

class Model3D(Base_Model):
    @property
    def facies_maps_index(self):
        return self.model_path / "in//ts1//bl1//faci_m//cont.pmt"
    @property
    def depth_maps_index(self):
        return self.model_path / "in//ts1//bl1//dpth_m//cont.pmt"
    @property
    def heatflow_maps_index(self):
        return self.model_path / "in//hf_m//cont.pmt"
    @property
    def heatflow_maps(self):
        return self.model_path / "in//hf_m"
    @property
    def active_heatflow_model(self):
        return self.model_path / "in//heat.pmt"
    @property
    def active_pwd_model(self):
        return self.model_path / "in//palg.pmt"
    @property
    def pwd_maps(self):
        return self.model_path / "in//pdp_m"
    @property
    def pwd_maps_index(self):
        return self.model_path / "in//pdp_m//cont.pmt"
    @property
    def depth_maps(self):
        return self.model_path / "in//ts1//bl1//dpth_m"  # for subsheat building
    @property
    def facies_maps(self):
        return self.model_path / "in//ts1//bl1//faci_m"  
    @property
    def facies_table(self):
        return self.model_path / "in//uni3.pmt"

    @property
    def sub_version(self):
        version = []
        fullpath = self.model_path / "in//layerdef.pmt"
        while len(version) == 0:
            with (open(fullpath)) as f:
                for line in f:
                    if line.startswith("c Age Assignment"):
                        version.append(line)
                        break
        version = str(version[0])
        startind = version.find("PetroMod ")
        version = version[startind + 9 : -2]
        return version
    @property
    def geometry(self):
        layerdef = Utils.read_pmt(self.model_path / "in//layerdef.pmt")
        horizongeom = Utils.read_pmt(self.model_path / "in//ts1//bl1//horizongeom.pmt")
        horizongeom = horizongeom[["HorizonID", "HorizonGeomID", "FaciesMapID"]]
        df = layerdef.merge(horizongeom, on="HorizonID")
        df = df[df.HorizonAge != 99999.0]
        return df

    @property
    def grid_size(self):
        aoi_table = Utils.read_pmt(self.depth_maps_index)
        aoi_file_name = aoi_table.ID[0]
        aoi_file_name = str(aoi_file_name)
        aoi_file_name = aoi_file_name + ".pmd"
        aoi_map_path = self.depth_maps / aoi_file_name
        aoi = xtgeo.surface_from_file(aoi_map_path, fformat="petromod")
        return {"xinc": aoi.xinc, "yinc": aoi.yinc}

    
    def get_heatflow_age(self):
        try:
            df = Utils.read_pmt(self.active_heatflow_model)
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
        if self.heatflow_maps_index.exists():
            df = self.get_heatflow_maps_index()
            max_id = df["ID"].max() + 1
        else:  # create new
            if self.heatflow_maps.exists() == False:
                logger.info(
                    "Heat flow maps folder does not exist. Creating an empty folder..."
                )
                os.mkdir(self.heatflow_maps)
            else:
                logger.info("No heatflow map index file found. Creating cont.pmt..")
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
            fname = str(max_id) + ".pmd"
            filepath = self.heatflow_maps / fname
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
        output = Utils.write_pmt("Standard Content", df, 4, headers,self.sub_version)
        with open(self.heatflow_maps_index, "w+") as f:
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
        output = Utils.write_pmt("Heat Flow", df, 5, headers,self.sub_version)
        with open(self.active_heatflow_model, "w+") as f:
            f.write(output)
        return

    def get_heatflow_maps_index(self):
        try:
            df = Utils.read_pmt(self.heatflow_maps_index)
            while df.shape[1] > 4:
                df = df.drop(df.columns[-1], axis=1)
        except:
            raise Exception("No heatflow maps in PM")
        return df



    def add_paleo_water_depth_maps(
        self, map_dict, folder_name=None, update_model=False
    ):
        """[summary]

        Args:
            map_dict (dict): Dictionary containing: Keys: Age of map in string. Value: PWD map in xtgeo surface object
            folder_name (str, optional): Name of folder of maps in PetroMod. Defaults to None.
            update_model (bool, optional): Set PWD maps to active in PetroMod. Defaults to False.
        """
        # Check existing pwd map index
        if self.pwd_maps_index.exists():
            df = self.get_pwd_maps_index()
            max_id = df["ID"].max() + 1
        else:  # create new
            if self.pwd_maps.exists() == False:
                logger.info(
                    "Paleo Water Depth maps folder does not exist. Creating an empty folder..."
                )
                os.mkdir(self.pwd_maps)
            else:
                logger.info(
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
            fname = str(max_id) + ".pmd"
            filepath = self.pwd_maps / fname
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
        output = Utils.write_pmt("Standard Content", df, 4, headers,self.sub_version)
        with open(self.pwd_maps_index, "w+") as f:
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
        output = Utils.write_pmt("Water Depth / Paleo Depth", df, 7, headers,self.sub_version)
        with open(self.active_pwd_model, "w+") as f:
            f.write(output)
        return

    def get_pwd_age(self):
        try:
            df = Utils.read_pmt(self.active_pwd_model)
            df = df["AgeFrom"].values
            df = df.astype(int)
        except:
            raise Exception(
                "No Paleo-water depth table in PM. Open PM and create table first"
            )
        return df

    def get_pwd_maps_index(self):
        try:
            df = Utils.read_pmt(self.pwd_maps_index)
            while df.shape[1] > 4:
                df = df.drop(df.columns[-1], axis=1)
        except:
            raise Exception("No Paleo-water depth maps in PM")
        return df

    def get_facies_table(self):
        try:
            df = Utils.read_pmt(self.facies_table)
        except:
            raise Exception("No facies defined in PM. Open PM and create table first")
        return df




