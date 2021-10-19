from .utils import Utils
from .project_data import Project_data
from .logging import logger
class Base_Model:
    def __init__(self,model_path):

        self.model_path = model_path
    @property
    def model_path(self):
        """Pathlib path to the model"""
        return self._model_path
    
    @model_path.setter
    def model_path(self,path):
        if path.exists() == False:
            logger.critical("Model does not exist")
        self._model_path = path
        self._project_path = self._model_path.parents[1]
        self._ndim=Utils.check_ndim(self._model_path)
        if self._ndim != 1:
            self._check_sublayer()
        self._version = Utils.get_version(self._project_path)
        self._project_data=Project_data(self._project_path)
        return

    @property
    def project_data(self):
        """Project data
        Returns
        -------
        Project data class
            Project data
        """
        return self._project_data
    @property
    def version(self):
        """Major version of the project

        Returns
        -------
        str
            Major version of the project
        """
        return self._version
    def _check_sublayer(self):
        sublayer = False
        sublayer_path = self._model_path / "in//ts1//bl1//subl.pmt"
        if sublayer_path.exists():
            df = Utils.read_pmt( self._model_path / "in//ts1//bl1//subl.pmt")
            df = df.groupby("LayerID").FaciesMapID.nunique() > 1
            a = df[df].index.tolist()
            if len(a) != 0:
                sublayer = True
            else:
                pass
        self.sublayer = sublayer
        return
