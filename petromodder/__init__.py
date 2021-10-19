from .project import Project
from .models import get_model
from .model3D import Model3D
from .project_data import Project_data

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass