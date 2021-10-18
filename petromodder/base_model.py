from .utils import Utils
from .project_data import Project_data
from .logging import logger
class Base_Model:
    def __init__(self,model_path):
        """Base class of all model

        :param model_path: Path to the model
        :type model_path: Pathlib.PoxisPath/Pathlib.WindowsPath
        """
        self.model_path = model_path
    @property
    def model_path(self):
        return self.__model_path
    
    @model_path.setter
    def model_path(self,path):
        if path.exists() == False:
            logger.critical("Model does not exist")
        self.__model_path = path
        self.__project_path__ = self.__model_path.parents[1]
        self.ndim=Utils.check_ndim(self.__model_path)
        if self.ndim != 1:
            self._check_sublayer()
        self.version = Utils.get_version(self.__project_path__)
        self.project_data=Project_data(self.__project_path__)
        return



    def _check_sublayer(self):
        sublayer = False
        sublayer_path = self.__model_path / "in//ts1//bl1//subl.pmt"
        if sublayer_path.exists():
            df = Utils.read_pmt( self.__model_path / "in//ts1//bl1//subl.pmt")
            df = df.groupby("LayerID").FaciesMapID.nunique() > 1
            a = df[df].index.tolist()
            if len(a) != 0:
                sublayer = True
            else:
                pass
        self.sublayer = sublayer
        return
