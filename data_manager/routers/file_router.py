'''
Created on 17 mar. 2020

@author: victor
'''
from flask import send_from_directory

from helper import config as cfg
from helper import utils
   

class FileRouter:
    """A class that represents the router in charge of handling DataManager API File Blueprint methods
    """
    def get_file_by_filename(self, filename):
        """Gets the file correspondent to a specific filename in server
        
        API Endpoint: '/videoAnalysis/files/<filename>', methods=['GET']
        
        :param filename: Name of file
        :type filename: str
        :return: Response containing file requested
        :rtype: flask.Response
        """
        folder_file = ""
        for folder, extension_list in cfg.dict_filetypes.items():
            for extension in extension_list:
                if extension in filename:
                    folder_file = folder
                    break
        folder_abspath = f"{cfg.data_manager_path}/static/{folder_file}"
        return send_from_directory(folder_abspath, filename=filename, as_attachment=True)