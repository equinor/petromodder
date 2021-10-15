from .utils import Utils
from .model3D import Model3D
from .logging import logger

def get_model(model_path):
    model_path = Utils.path_checker(model_path)
    ndim = Utils.check_ndim(model_path)
    if ndim == 3:
        model = Model3D(model_path)
    else:
        logger.warning("Only 3D model is supported at the moment")
    return model



