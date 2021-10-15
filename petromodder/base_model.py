from .utils import Utils
from .project_data import Project_data
from .logging import logger
class Base_Model:
    def __init__(self,model_path):
        self.model_path = model_path
    @property
    def model_path(self):
        return self.__model_path__
    
    @model_path.setter
    def model_path(self,path):
        if path.exists() == False:
            logger.critical("Model does not exist")
        self.__model_path__ = path
        self.__project_path__ = self.__model_path__.parents[1]
        self.ndim=Utils.check_ndim(self.__model_path__)
        if self.ndim != 1:
            self.check_sublayer()
        self.version = Utils.get_version(self.__project_path__)
        self.project_data=Project_data(self.__project_path__)
        return



    def check_sublayer(self):
        """Check if the model contains different properties for sublayers
        """
        sublayer = False
        sublayer_path = self.__model_path__ / "in//ts1//bl1//subl.pmt"
        if sublayer_path.exists():
            df = Utils.read_pmt( self.__model_path__ / "in//ts1//bl1//subl.pmt")
            df = df.groupby("LayerID").FaciesMapID.nunique() > 1
            a = df[df].index.tolist()
            if len(a) != 0:
                sublayer = True
            else:
                pass
        self.sublayer = sublayer
        return
    @property
    def lithology(self):
        return self.__project_data__.lithology
    @property
    def block_boundaries(self):
        return self.__project_data__.block_boundaries 
    @property
    def polygons(self):
        return self.__project_data__.polygons   
    @property
    def crosslines(self):
        return self.__project_data__.crosslines 