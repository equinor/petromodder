from .cultural_data import Cultural_data
from .lithology import Lithology
class Project_data:
    def __init__(self,project_data_path):
        self.__project_data_path = project_data_path
    @property
    def cultural_data(self):
        return Cultural_data(self.__project_data_path)
    @property
    def lithology(self):
        return Lithology(self.__project_data_path).lithology

