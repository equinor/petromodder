from .cultural_data import Cultural_data
from .lithology import Lithology
class Project_data:
    def __init__(self,project_data_path):
        self.__project_data_path = project_data_path
    @property
    def cultural_data(self):
        """Cultural data of the project

        Returns
        -------
        Cultural_data class
            Cultural data of the project
        """
        return Cultural_data(self.__project_data_path)
    @property
    def lithology(self):
        """Lithology database of the project

        Returns
        -------
        dict
            Project's lithology data
        """
        return Lithology(self.__project_data_path).lithology

