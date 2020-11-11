'''
Created on 17 mar. 2020

@author: victor
'''
import traceback
import time
import json

from helper import config as cfg
from helper import global_variables as gv
from helper import utils
from managers.memory_emergency_manager import MemoryEmergencyManager


class DocumentRouter:
    """A class that represents the router in charge of handling DataManager API Documents Blueprint methods

    :param document_manager: DbManager in charge of handling ProbeConfig documents in MongoDB
    :type document_manager: managers.db_managers.DocumentDbManager
    :param videoqualitypred_manager: Manager in charge of handling requests to the Video Quality Analysis AI Module
    :type videoqualitypred_manager: managers.VideoQualityPredManager
    """
    
    def __init__(self, document_manager, videoqualitypred_manager):
        """Constructor
        
        """
        self.document_manager = document_manager
        self.videoqualitypred_manager = videoqualitypred_manager
        self.input_document = None
        self.memory_emergency_manager = MemoryEmergencyManager()
        
        
    def bulk_document_to_db(self, input_document, headers):
        """Insert document from VideoQualityProbe into the database.
        Includes the prediction process from VideoQA
        
        API Endpoint: '/videoAnalysis/documents/bulk', methods=['POST']

        :param body: Body from the request
        :type body: str
        :param headers: Headers at the request
        :type headers: dict
        :return: Response of the method
        :rtype: dict
        """
        task = cfg.bulk_data_task
        document = None
        status = 200
        try:
            self.input_document = input_document
            self.add_confidence_interval()
            response_mos_analyzer = self.videoqualitypred_manager.post_api_mos_analyzer(
                self.input_document, headers)
            if response_mos_analyzer.status_code == 200:
                document = self.videoqualitypred_manager.prepare_data_to_db(
                    data_content_input=self.input_document,
                    data_content_output=response_mos_analyzer.text,
                    headers=headers
                )
            # Write to MongoDB
            doc_id = self.document_manager.insert_video_analysis_document(document=document)
            if gv.api_dm.probe_status in ["stopped", "idle", "error"]:
                gv.api_dm.probe_status = "running"
            if doc_id is None:
                status = 404
            gv.api_dm.last_document_time = time.time()
            response = utils.build_output(task=task, status=status, message=cfg.success_msg, output={"document ID": str(doc_id)})
            MemoryEmergencyManager.check_memory_status()
        except Exception as e:
            status = 500
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
            response = utils.build_output(task=task, status=500, message=str(e), output={})
        return response, status

    def add_confidence_interval(self):
        input_document_dict = json.loads(self.input_document)
        input_document_dict.update({"confidence_intervals": cfg.confidence_percentage})
        self.input_document = json.dumps(input_document_dict)
    
    def get_document_by_id(self, id):
        """Gets a document (measure) from the DB
        
        API Endpoint: '/videoAnalysis/document/<docId>', methods=['GET']

        :param id: ID of the document
        :type id: int
        :return: Document containing a measure
        :rtype: dict
        """
        document = None
        try:
            document = self.document_manager.get_document_by_id(id=id)
        except Exception as e:
            gv.logger.error(e)
        return document

    def get_last_video_analysis_document(self):
        """Gets the last document inserted at the database
        
        API Endpoint: '/videoAnalysis/documents/last', methods=['GET']

        :return: Latest document containing a measure
        :rtype: dict
        """
        document = None
        try:
            
            document = self.document_manager.get_last_video_analysis_document()
        except Exception as e:
            gv.logger.error(e)
        return document