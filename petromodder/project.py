from .utils import Utils
from .models import get_model
from .project_data import Project_data
import os
class Project:
    def __init__(self,project_path):
        self.project_path = project_path
    @property
    def project_path(self):
        return self.__project_path__

    @project_path.setter
    def project_path(self,path):
        path=Utils.path_checker(path)
        self.__project_path__=path
        self.__validate_project__()
        self.__project_data__ = Project_data(self.__project_path__)
        return


    def __validate_project__(self):
        folders_to_check = ['cult','data','def','geo','well','pm1d','pm2d','pm3d']
        check = 0
        for name in os.listdir(self.__project_path__):
            if name in folders_to_check:
                check +=1
        if check != len(folders_to_check):
            raise Exception
        self.version = Utils.get_version(self.__project_path__)
        return
    

    @property
    def models_1D(self):
        path = self.project_path/'pm1d'
        if path.exists():
            models = os.listdir(path)
            models = {i:self.project_path/'pm1d'/i for i in models}
        else:
            models = {}
        return models
    @property
    def models_2D(self):
        path = self.project_path/'pm2d'
        if path.exists():
            models = os.listdir(path)
            models = {i:self.project_path/'pm2d'/i for i in models}
        else:
            models = {}
        return models
    @property
    def models_3D(self):
        path = self.project_path/'pm3d'
        if path.exists():
            models = os.listdir(path)
            models = {i:self.project_path/'pm3d'/i for i in models}
        else:
            models = {}
        return models
    
    @property
    def lithology(self):
        return self.__project_data__.lithology
    @property
    def cultural_data(self):
        return self.__project_data__.cultural_data

    