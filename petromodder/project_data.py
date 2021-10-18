from .cultural_data import Cultural_data
from .lithology import Lithology
class Project_data:
    def __init__(self,project_data_path):
        """Project level data

        :param project_data_path: Path to the project
        :type project_data_path: Pathlib.PoxisPath/Pathlib.WindowsPath
        """
        self.__project_data_path = project_data_path
    @property
    def cultural_data(self):
        """Cultural data of the project

        :return: Cultural data
        :rtype: Cultural data object
        """
        return Cultural_data(self.__project_data_path)
    @property
    def lithology(self):
        """Lithology data of the project

        :return: Lithology data
        :rtype: dict
        """
        return Lithology(self.__project_data_path).lithology

