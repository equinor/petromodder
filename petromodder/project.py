from .utils import Utils
from .models import get_model
from .project_data import Project_data
import os
class Project:
    """PetroMod project object
    """
    def __init__(self,project_path):
        self.project_path = project_path
    @property
    def project_path(self):
        """Path to project

        Returns
        -------
        Pathlib.PoxisPath/Pathlib.WindowsPath
            Pathlib path to the project
        """
        return self._project_path

    @project_path.setter
    def project_path(self,path):
        path=Utils.path_checker(path)
        self._project_path=path
        self._validate_project()
        self.__project_data = Project_data(self._project_path)
        return


    def _validate_project(self):
        folders_to_check = ['cult','data','def','geo','well','pm1d','pm2d','pm3d']
        check = 0
        for name in os.listdir(self._project_path):
            if name in folders_to_check:
                check +=1
        if check != len(folders_to_check):
            raise Exception
        self._version = Utils.get_version(self._project_path)
        return
    
    @property
    def version(self):
        """Major version of the project

        Returns
        -------
        str
            Major version of the project
        """
        return self._version
    @property
    def models_1D(self):
        """list of all 1D model

        Returns
        -------
        dict
            key = model name, value: Pathlib path to the model
        """
        path = self.project_path/'pm1d'
        if path.exists():
            models = os.listdir(path)
            models = {i:self.project_path/'pm1d'/i for i in models}
        else:
            models = {}
        return models
    @property
    def models_2D(self):
        """list of all 2D model

        Returns
        -------
        dict
            key = model name, value: Pathlib path to the model
        """
        path = self.project_path/'pm2d'
        if path.exists():
            models = os.listdir(path)
            models = {i:self.project_path/'pm2d'/i for i in models}
        else:
            models = {}
        return models
    @property
    def models_3D(self):
        """list of all 3D model

        Returns
        -------
        dict
            key = model name, value: Pathlib path to the model
        """
        path = self.project_path/'pm3d'
        if path.exists():
            models = os.listdir(path)
            models = {i:self.project_path/'pm3d'/i for i in models}
        else:
            models = {}
        return models
    
    
    @property
    def project_data(self):
        """Project data
        Returns
        -------
        Project data class
            Project data
        """
        return self.__project_data

    