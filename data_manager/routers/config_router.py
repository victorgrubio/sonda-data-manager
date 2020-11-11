'''
Created on 17 mar. 2020

@author: victor
'''
import subprocess
import traceback
import json
from helper import global_variables as gv
from helper import config as cfg
from helper import utils

class ConfigRouter:
    """A class that represents the router in charge of handling DataManager API Probe/config Blueprint methods
        
    :param config_manager: DbManager in charge of handling ProbeConfig documents in MongoDB
    :type config_manager: managers.db_managers.ConfigDbManager
    """
    
    def __init__(self, config_manager):
        """Constructor
        """
        self.config_manager = config_manager
        
    def get_config_videoqualityprobe(self):
        """Gets the current config of the VideoQualityProbe

        API Endpoint: '/videoAnalysis/probe/config', methods=['GET']
        
        :return: Config as a dict
        :rtype: dict
        """
        config = None
        try:
            config = self.config_manager.get_config() 
        except AttributeError:
            raise AttributeError("No config data in DB")
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return config.to_json()
    

    def put_config_videoqualityprobe(self, config_json):
        """Updates the current config using a JSON document

        API Endpoint: '/videoAnalysis/probe/config', methods=['PUT']
        
        :param config_json: JSON document containing the config
        :type config_json: str
        :raises Exception: Generic Error
        """
        gv.logger.info(config_json)
        if isinstance(config_json, str):
            config_data= json.loads(config_json)
        elif isinstance(config_json, dict):
            config_data = config_json
        else:
            raise Exception(f"Config json input has invalid data type {type(config_json)}. Must be JSON (str) or dict")
        self.config_manager.put_config(config_data)
    

    def get_mux_program_numbers(self, url):
        program_numbers_json_bytes = subprocess.check_output([
            "ffprobe", "-i",
            url, "-loglevel", "quiet",
            "-show_entries", "program=program_id:program_tags=service_name", 
            "-of", "json"  
        ])
        program_numbers_json = json.loads(program_numbers_json_bytes.decode("utf-8"))
        output_programs = []
        for program in program_numbers_json["programs"]:
            output_programs.append({
                "program_id": program["program_id"],
                "channel": program["tags"]["service_name"]
            })
        return output_programs