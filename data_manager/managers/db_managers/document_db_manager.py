'''
Created on 16 mar. 2020

@author: victor
'''
from mongoengine import DoesNotExist, MultipleObjectsReturned
import json
import pytz
import traceback
import time
import psutil
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId

from managers.db_managers import BaseDbManager
from helper import global_variables as gv
from helper import config as cfg
from db_models import Journey, Program, StatusData, VideoAnalysis, Alert, Warn


class DocumentDbManager(BaseDbManager):
    """Class that represents the handler object use to manage Alerts in MongoDB

    :param db_connection: DbConnection instance to handle MongoDb connection
    :type db_connection: data_manager.managers.DbConnection
    :param config_manager: MongoDb handler that manages config
    :type config_manager: data_manager.managers.db_managers.ConfigDbManager
    :param journey_manager: MongoDb handler that manages journeys
    :type journey_manager: data_manager.managers.db_managers.JourneyDbManager
    :param program_manager: MongoDb handler that manages programs
    :type program_manager: data_manager.managers.db_managers.ProgramDbManager
    :param alert_manager: MongoDb handler that manages alerts
    :type alert_manager: data_manager.managers.db_managers.AlertDbManager
    """
    def __init__(self, db_connection, config_manager, journey_manager, program_manager, alert_manager):
        """Constructor
        """
        BaseDbManager.__init__(self, db_connection)
        self.config_manager = config_manager
        self.journey_manager = journey_manager
        self.program_manager = program_manager
        self.alert_manager = alert_manager
        self.last_document_id = ""
        self.videoanalysis_db_document = None # VideoAnalysis Document
        self.last_db_document = None # VideoAnalysis Document
    
    def insert_video_analysis_document(self, document=None):
        """Inserts the analysis document into the DB
        
        :param document: Analysis document
        :type document: dict
        :return: The id of the document inserted in db
        :rtype: ObjectId
        """
        self.check_db()
        try:
            self.videoanalysis_db_document = VideoAnalysis(**document)
            journey = self.get_journey_of_document()
            self.update_videoanalysis_document_fields()
            self.check_program_of_document()
            self.journey_manager.update_journey_data(journey, self.videoanalysis_db_document)
            # Create indexes for query speed-up
            _ = self.db_connection.db.video_analysis.create_index([("inserted_at", -1)])
            _ = self.db_connection.db.video_analysis.create_index([("journey_datetime", -1)])
            self.videoanalysis_db_document.journey_datetime = self.journey_manager.journey_datetime
            self.videoanalysis_db_document.save()
            # search for alerts and warnings
            self.alert_manager.find_alerts_warnings(self.videoanalysis_db_document)
        except Exception as e:
            gv.logger.error(e)
            traceback.print_exc()
        return str(self.videoanalysis_db_document.id)

    def update_videoanalysis_document_fields(self):
        current_status = StatusData.objects.order_by('-id').first()
        self.videoanalysis_db_document.videoSRC.url = current_status.url
        self.videoanalysis_db_document.videoSRC.service_name = self.config_manager.config.channel_name
        self.videoanalysis_db_document.journey_datetime = self.journey_manager.journey_datetime
        self.videoanalysis_db_document.content_type = current_status.content_type
        self.videoanalysis_db_document.videoSRC.program_name = self.program_manager.check_current_program_name()
            
    def get_journey_of_document(self):
        """Checks the journey correspondent to the current document inserted in the DB
        
        :return: Current journey
        :rtype: db_models.Journey
        """
        journey = None
        try:
            current_status = StatusData.objects.order_by('-id').first()
            if current_status.probe_status in ["idle", "stopped"]:
                gv.api_dm.probe_status = "running"
            self.journey_manager.set_journey_datetime()
            journey = Journey.objects(journey_datetime=self.journey_manager.journey_datetime).get()
        except DoesNotExist:
            # Creates a new one
            journey = self.journey_manager.add_new_journey(current_status)
        except MultipleObjectsReturned:
            latest_journey = Journey.objects.order_by('-id').first()
            latest_journey.delete()
            gv.logger.warning("Multiple journeys, removing corrupted data from import")
        return journey
    
    def check_program_of_document(self):
        """Checks the journey correspondent to the current document inserted in the DB
        
        :param document: Analysis document, as a dict
        :type document: dict
        :return: Current program
        :rtype: db_models.Program
        """
        program = None
        program_name = None
        try:
            program_name = self.program_manager.check_current_program_name()
            program = Program.objects(
                program_name=program_name, journey_datetime=self.journey_manager.journey_datetime).get()
            if program is None:
                self.program_manager.add_new_program(self.videoanalysis_db_document)
                gv.logger.info("Inserted new program on DB")
            else:
                self.program_manager.update_program_in_db(self.videoanalysis_db_document, program)
        except DoesNotExist:
            self.program_manager.add_new_program(self.videoanalysis_db_document)
            gv.logger.info("New program name {}".format(program_name))
            gv.logger.info("Inserted new program on DB due to DoesNotExist exception")
        except MultipleObjectsReturned:
            latest_program = Program.objects.order_by('-id').first()
            latest_program.delete()
            gv.logger.info("Multiple programs, removing corrupted data from import")

    def get_last_video_analysis_document(self):
        """Gets the last video_analysis document introduced in db
        
        :return: Last VideoAnalysis introduced as a dict
        :rtype: dict
        """
        document = None
        try:
            self.last_db_document = VideoAnalysis.objects.order_by('-_id').first()
            document = self.get_last_document()
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return document
    
    def get_last_document(self):
        last_document_time_difference = time.time() - gv.api_dm.last_document_time
        if gv.api_dm.probe_status == "error":
            return None
        # If we are starting and 30 seconds have passed without any document, generates an error
        if gv.api_dm.probe_status in ["idle"] and last_document_time_difference > cfg.start_delay:
            _ = gv.api_dm.probe_router.kill_probe_process()
            gv.api_dm.probe_status = "error"
            gv.logger.warn("Status has been set to ERROR")
            return None
        if self.last_db_document is None:
            return {}  
        self.check_no_content(last_document_time_difference)
        document = json.loads(self.last_db_document.to_json(use_db_field=False))
        # Convert to string
        if isinstance(document['_id'], ObjectId):
            document['_id'] = str(document['_id'])
        self.last_document_id = str(self.last_db_document.id)
        return document
        
    def check_no_content(self, last_document_time_difference):
        # If then last document was the same for more than 1+1/3 of sample time, generates an alert.
        if self.is_document_old_and_probe_stopped(last_document_time_difference):
            alert = {
                "category": "Content",
                "description":cfg.dict_alert_category_description["Content"],
                "alert_type":"alert",
                "duration": int(last_document_time_difference)
            }
            self.alert_manager.document = self.last_db_document
            self.alert_manager.create_document_alert(alert)

    def is_document_old_and_probe_stopped(self, last_document_time_difference):
        current_status = StatusData.objects.order_by('-id').first()
        if current_status.content_type != "live":
            return False
        same_document_in_db = self.last_document_id == str(self.last_db_document.id)
        no_documents_in_3_measure_time = last_document_time_difference > (float(cfg.probe_measure_seconds)*3 + float(cfg.probe_measure_seconds)/3)
        is_probe_running = psutil.pid_exists(current_status.probe_pid)
        if same_document_in_db and no_documents_in_3_measure_time and is_probe_running:
            return True

        return False