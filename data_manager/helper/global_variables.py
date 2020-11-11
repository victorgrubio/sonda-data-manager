import os
from helper.custom_log import init_logger
from managers.api_manager import DataManagerAPI
"""Global variables declaration and initialization for complete DataManager module
"""

global_parent_dir = None
logger = None
api_dm = None

def init(parent_dir, log_level="INFO"):
    """Initializes global variables
    
    :param parent_dir: Dir to define as root
    :type parent_dir: str
    :param log_level: Minimum level to represent logs, defaults to "INFO"
    :type log_level: str, optional
    """
    global global_parent_dir
    global logger
    global api_dm

    global_parent_dir = parent_dir
    os.environ['videoQA_parentDir'] = global_parent_dir
    logger = init_logger(__name__, log_level=log_level)
    api_dm = DataManagerAPI()