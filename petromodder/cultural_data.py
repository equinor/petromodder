import os
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from .utils import Utils
from .logging import logger
class Cultural_data:
    def __init__(self,project_path):
        self.__cultural_path = project_path/ "cult"
    @property
    def block_boundaries(self):
        exist = False
        for f in os.listdir(self.__cultural_path):
            if f == "blockbound.pmt":
                exist = True
                break
        if exist == True:
            polygons = self.make_polygons("blockbound.pmt")
        else:
            polygons = None
            logger.info("No crossline in the project")
        return polygons
    @property
    def polygons(self):
        exist = False
        for f in os.listdir(self.__cultural_path ):
            if f == "line.pmt":
                exist = True
                break
        if exist == True:
            polygons = self.make_polygons("line.pmt")
        else:
            polygons = None
            logger.info("No polygon in the project")
        return polygons
    @property
    def crosslines(self):
        exist = False
        for f in os.listdir(self.__cultural_path ):
            if f == "crossline.pmt":
                exist = True
                break
        if exist == True:
            polygons = self.make_polygons("crossline.pmt")
        else:
            polygons = None
            logger.info("No crossline in the project")
        return polygons

    def make_polygons(self, item):
        """Make Shapely object from PetroMod polygons/lines
        
        Arguments:
            item {path} -- PetroMod PMT file containing polygons/lines
        
        Returns:
            dict -- key: polygon name, value: Shapely object
        """
        poly_all = {}
        line_all = {}
        fpath = self.__cultural_path  / item
        df = Utils.read_pmt(fpath)
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
        line_poly = {"polygon": poly_all, "lines": line_all}
        return line_poly