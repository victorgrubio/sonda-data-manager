'''
Created on 17 mar. 2020

@author: victor
'''
import traceback
import subprocess
from pathlib import Path
from flask import send_from_directory
from os import  getenv

from helper import config as cfg
from helper import global_variables as gv
from helper import utils


class DbRouter:
    """A class that represents the router in charge of handling DataManager API DB Blueprint methods
    """
    
    def import_db(self, db_request):
        """Imports DB from GZIP file in a request

        API Endpoint: '/videoAnalysis/db/import', methods=['POST']
        
        :param db_request: DB in GZIP format
        :type db_request: flask.Request
        :return: Generic message response with specific import db content
        :rtype: dict
        """
        try:
            f = db_request.files['file']  
            f.save("{}/{}".format(cfg.upload_path, f.filename))  
            command = [
                "mongorestore",
                "--port", getenv("DB_PORT"), 
                "--excludeCollection","probe_config",
                "--excludeCollection","status_data",
                "--gzip", f"--archive={cfg.upload_path}/{f.filename}"
            ]
            process = subprocess.Popen(command)
            process.wait()
            # self.dbManager.import_db(db_dict)
            response = utils.build_output(task=cfg.import_db_task, status=200,
                                         message=cfg.success_msg, output={})
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
            response = utils.build_output(task=cfg.import_db_task, status=500,
                                         message=str(e), output={})
        return response
    
    def export_db(self):
        """Exports DB to a GZIP file and sends it to the user

        API Endpoint: '/videoAnalysis/db/export', methods=['GET']
        
        :return: GZIP file containing database
        :rtype: flask.Response
        """
        
        filename = "db.gzip"
        command = [
            "mongodump",
            f"--archive={filename}",
            "--port", getenv("DB_PORT"),
            "--db", cfg.db_name,
            "--forceTableScan",
            "--excludeCollection","probe_config",
            "--excludeCollection","status_data",
            "--gzip"
        ]
        process = subprocess.Popen(command)
        process.wait()
        return send_from_directory(cfg.data_manager_path, filename=filename, as_attachment=True)