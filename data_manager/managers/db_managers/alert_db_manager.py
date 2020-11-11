from mongoengine import DoesNotExist, MultipleObjectsReturned, QuerySet, NotUniqueError
from datetime import datetime, timedelta, timezone
from collections import OrderedDict
from pyrfc3339 import parse, generate
import json
import pytz
from dateutil.tz import tzlocal

import time
import traceback

from managers.db_managers import BaseDbManager, AnomalyDbManager
from helper import global_variables as gv
from helper import config as cfg
from db_models import Alert, Warn, StatusData, Journey, Program, VideoAnalysis

class AlertDbManager(BaseDbManager):
    """Class that represents the handler object use to manage Alerts in MongoDB

    :param db_connection: DbConnection instance to handle MongoDb connection
    :type db_connection: data_manager.managers.DbConnection
    :param config_manager: MongoDb handler that manages config
    :type config_manager: data_manager.managers.db_managers.ConfigDbManager
    :param journey_manager: MongoDb handler that manages journeys
    :type journey_manager: data_manager.managers.db_managers.JourneyDbManager
    :param program_manager: MongoDb handler that manages programs
    :type program_manager: data_manager.managers.db_managers.ProgramDbManager
    """
    
    def __init__(self, db_connection, config_manager, journey_manager, program_manager):
        """Constructor
        """
        BaseDbManager.__init__(self, db_connection)
        self.config_manager = config_manager
        self.journey_manager = journey_manager
        self.program_manager = program_manager
        self.alert = None
        self.alert_dict_info_list = []
        self.last_alert_current_program = None
        self.last_alert_timestamp = 0.0
        self.document = None
        self.current_status = None
        self.create_indexes()
        self.anomaly_manager = AnomalyDbManager(db_connection, program_manager)

    def create_indexes(self):
        """Creates indexes to speed up the queries to the db
        """
        _ = self.db_connection.db.alert.create_index([ ("journey_datetime", -1) , ("program_name", -1)])
        _ = self.db_connection.db.alert.create_index([ ("journey_datetime", -1) , ("program_name", -1), ("document_id", -1)])
        _ = self.db_connection.db.warn.create_index([ ("journey_datetime", -1) , ("program_name", -1)])
        _ = self.db_connection.db.warn.create_index([ ("journey_datetime", -1) , ("program_name", -1), ("document_id", -1)])
            
    def find_alerts_warnings(self, document):
        """Checks if there is any alert or warning on the current analysis document
        
        :param document: db.VideoAnalysis correspondent the current analysis
        :type document: db_models.VideoAnalysis
        """
        try:
            self.check_db()
            self.document = document
            self.current_status = StatusData.objects.order_by('-id').first()
            # check each type of alert and adds them to the list
            self.check_video_audio_alerts()
            self.check_mos_alerts()
            self.check_blurring_alerts()
            self.check_lost_frames_alerts()
            self.generate_document_alerts() # Generates db documents
            self.alert_dict_info_list.clear() # Clear alerts for next document
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
    
    def check_video_audio_alerts(self):
        """Check if document has Video/Audio alerts/warnings"""
        alert_type = "alert"
        category = ""
        if self.document.videoSettings is None:
            category = "Video"
        if dict(self.document.audioSettings.to_mongo()) == cfg.no_audio_settings:
            category = "Audio"
        else:
            return
        self.append_alert_to_list(category, alert_type, cfg.probe_measure_seconds)
    
    def append_alert_to_list(self, category, alert_type, duration):
        alert_dict = {
            "category": category,
            "description": cfg.dict_alert_category_description[category],
            "alert_type": alert_type,
            "duration": duration
        }
        self.alert_dict_info_list.append(alert_dict)
    
    def check_mos_alerts(self):
        """Check if document has MOS alerts/warnings"""
        config = self.config_manager.config
        document_mos = self.document.mosAnalysis.mos
        alert_type = ""
        category = "MOS"
        if document_mos <= config.alert_mos_threshold:
            alert_type = "alert"
        elif document_mos > config.alert_mos_threshold and document_mos <= config.warning_mos_threshold:
            alert_type = "warning"
        else:
            return
        self.append_alert_to_list(category, alert_type, cfg.probe_measure_seconds)
        
    def check_blurring_alerts(self):
        """Check if document has Blurring alerts/warnings"""
        category = "Blurring"
        alert_type = ""
        if self.current_status.mode != "fast":
            # Blurring Alert
            if self.document.videoSettings.blurring_avg <= cfg.blurring_threshold_alert:
                alert_type = "alert"
            # Blurring Warning
            elif self.document.videoSettings.blurring_avg > cfg.blurring_threshold_alert and \
                self.document.videoSettings.blurring_avg <= cfg.blurring_threshold_warning:
                alert_type = "warning"
            else:
                return
            self.append_alert_to_list(category, alert_type, cfg.probe_measure_seconds)

    def check_lost_frames_alerts(self):
        category = "LostFrames"
        if self.document.lost_frames > 0:
            self.append_alert_to_list(category, "alert", duration=self.document.lost_frames)
            
    def generate_document_alerts(self):
        """Creates all alerts corresponding to current document
        """
        self.check_db()
        for alert in self.alert_dict_info_list:
            self.create_document_alert(alert)
    
    # TODO: ALERT AS ATTR

    def create_document_alert(self, alert):
        """Creates an alert from a document

        :param alert: Dict containing all information about data
        :type alert: dict
        """
        try:
            self.set_last_alert_current_program(alert)
            if self.last_alert_current_program is not None:
                self.check_alert_increment(alert)
            else:
                self.insert_new_alert_to_db(alert)
        # Either last document not found or last alert not found
        except (IndexError, DoesNotExist, AttributeError) as e: 
            gv.logger.info(e)
            self.insert_new_alert_to_db(alert)

    def set_last_alert_current_program(self, alert):
        """ """
        if alert["alert_type"] == "warning":
            self.last_alert_current_program = Warn.objects(
                journey_datetime=self.journey_manager.journey_datetime,
                program_name=self.program_manager.current_program_name,
                category=alert["category"]).order_by("-start_datetime").first()
        elif alert["alert_type"] == "alert":
            self.last_alert_current_program = Alert.objects(
                journey_datetime=self.journey_manager.journey_datetime,
                program_name=self.program_manager.current_program_name,
                category=alert["category"]).order_by("-start_datetime").first()
    
    def check_alert_increment(self, alert):
        """ 
        Checks if the alert correspond to a previous alert and increments its duration. If not, creates a new one
        :param alert: Dict containing all information about data
        :type alert: dict
        """
        if alert["category"] == "Content":
            self.check_content_alert_increment(alert)
        # For alerts with category different from content
        else:
            self.check_common_alert_increment(alert)

    def check_content_alert_increment(self, alert):
        """For content error , does not check time as it has been already consulted
           Updating alert as difference between alerts is lower than a measure (two consecutive documents)

        :param alert: Dict containing all information about data
        :type alert: dict
        """
        gv.logger.warning("Checking Content ALERT increment")
        last_alert_timestamp = datetime.timestamp(
            self.last_alert_current_program.end_datetime.replace(tzinfo=pytz.utc).astimezone(pytz.utc))
        if (time.time() - last_alert_timestamp) < float(cfg.probe_measure_seconds):
            self.update_content_alert()
        # If difference > measure time -> new content alert
        else:
            self.insert_new_alert_to_db(alert)

    def update_content_alert(self):
        gv.logger.warning("Updating no content ALERT")
        self.last_alert_current_program.update(
            # Mean mos value
            end_datetime=datetime.now(tzlocal()),
            duration=int(time.time() - gv.api_dm.last_document_time - int(cfg.probe_measure_seconds))
        )
    
    def check_common_alert_increment(self, alert):
        """Checks if the difference between documents with same alert category is lower than measure time + 1sec
        
        :param alert: Dict containing all information about data
        :type alert: dict
        """
        if self.is_same_alert(alert):
            self.update_existing_alert(alert)
        # If not, generates new alert as they are two separate documents with no alert documents between them
        else:
            self.insert_new_alert_to_db(alert)

    def is_same_alert(self, alert):
        if self.last_alert_current_program.video_second is not None: # VOD
            # difference between the document videosecond and the previous alert
            time_difference =  self.document.videoSettings.video_second - (
                self.last_alert_current_program.video_second + self.last_alert_current_program.duration
            )
            return time_difference < int(cfg.probe_measure_seconds)
        return self.check_is_same_alert_live(alert)
    
    def check_is_same_alert_live(self, alert):
        # As it is a db object, we have to make this replacement because it doesn't get the timze
        # in the query. Is always saved as UTC, the replacement is always the same
        last_alert_timestamp = datetime.timestamp(
            self.last_alert_current_program.end_datetime.replace(tzinfo=pytz.utc).astimezone(pytz.utc))
        time_difference = abs(last_alert_timestamp - (self.document.inserted_at / 1000))
        # Difference = 2*measure_time
        if time_difference < (2*float(cfg.probe_measure_seconds)):
            return True
        return False

    def update_existing_alert(self, alert):
        """Updates an existing_alert

        :param alert: Dict containing all information about data
        :type alert: dict
        """
        gv.logger.warning(f"UPDATING LAST {alert['alert_type']} of category {alert['category']}")
        # update mos values for alert
        mos_increase = self.document.mosAnalysis.mos / (self.last_alert_current_program.duration + 1)
        mos_alert = self.last_alert_current_program.mos*self.last_alert_current_program.duration
        mos_actual = mos_alert / (self.last_alert_current_program.duration + 1)
        duration = self.get_updated_alert_duration()
        self.last_alert_current_program.update(
            # Mean mos value
            mos = mos_actual + mos_increase,
            end_datetime=datetime.now(tzlocal()),
            duration=duration
        )
        # Save db object and reloads it to use in future methods
        self.last_alert_current_program.save()
        self.last_alert_current_program.reload()

    def get_updated_alert_duration(self):
        if self.document.videoSettings.video_second is not None:
            return self.last_alert_current_program.duration + int(cfg.probe_measure_seconds)
        located_last_alert_start_datetime = self.last_alert_current_program.start_datetime.replace(tzinfo=pytz.UTC)
        total_alert_duration_timedelta = datetime.now(pytz.UTC) - located_last_alert_start_datetime
        return total_alert_duration_timedelta.seconds
    
    def insert_new_alert_to_db(self, alert):
        """Adds new alert document into the DB
        
        :param alert: Dict containing all information about data
        :type alert: dict
        """
        alert_dict = {
            "journey_datetime": self.journey_manager.journey_datetime,
            "program_name": self.program_manager.current_program_name,
            "document_id": self.document.id,
            "duration": alert["duration"],
            "start_datetime": datetime.now(tzlocal()),
            "end_datetime": datetime.now(tzlocal()),
            "category": alert["category"],
            "description": alert["description"],
            "confidence": 100.0,
            "mos": self.document.mosAnalysis.mos,
            "url": "images/{}_{}.png".format(alert["alert_type"].lower(), alert["category"].lower())
        }
        if alert["category"] == "Blurring":
            alert_dict["confidence"] = 100 - self.document.videoSettings.blurring_avg
        alert_dict = self.add_alert_content_duration(alert_dict, alert["category"])
        if self.document.videoSettings.video_second is not None:
            alert_dict.update({"video_second": self.document.videoSettings.video_second})
        self.save_alert_type(alert_dict, alert["alert_type"])

    def add_alert_content_duration(self, alert_dict, category):
        """Enter duration for content alert"""
        if category == "content":
            # Gets the total time difference of the content
            alert_dict["duration"] = int(time.time() - gv.api_dm.last_document_time - int(cfg.probe_measure_seconds))
        return alert_dict

    def save_alert_type(self, alert_dict, alert_type):
        """Save alert depending on its type"""
        try:
            self.save_alert(alert_dict, alert_type)
        except NotUniqueError:
            gv.logger.warning(f"Trying to save a duplicate {alert_type} of category {alert_dict['category']}")
            # For content alerts the document may be the same as the probe is stopped
            # If this exception occurs then we update the last alert
            if alert_dict["category"] == "content":
                self.update_content_alert()

    def save_alert(self, alert_dict, alert_type):
        if alert_type == "alert":
            alert = Alert(**alert_dict) #Gets content of alert ddict into object (dbModel)
            alert.save()
        elif alert_type == "warning":
            warn = Warn(**alert_dict) #Gets content of warning ddict into object (dbModel)
            warn.save()
        gv.logger.warning(f"NEW {alert_type} of category {alert_dict['category']}")
        
    def get_alert_warning_list(self, journey_datetime=None, program_name=None):
        """Gets the list of alerts and warning documents from a concrete Journey or Program
        
        :param journey_datetime: Datetime of a Journey, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :param program_name: Name of a program, defaults to None
        :type program_name: str, optional
        :return: A list of db_models.Alert and db.models.Warning objects from MongoDB 
        :rtype: list
        """
        self.check_db()
        alert_dict = {"alerts": [], "warnings": []}
        db_alerts = {"alerts": [], "warnings": []}
        try:
            # Obtains program and journey from the db
            (journey_datetime, program_name) = self.program_manager.check_journey_and_program(journey_datetime, program_name)
            db_alerts = self.get_db_alerts(journey_datetime, program_name)
            if self.is_empty_db_alerts(db_alerts, program_name, journey_datetime):
                return {}
            else:
                alert_dict = self.update_alert_dict(alert_dict, db_alerts)
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return alert_dict

    def get_db_alerts(self, journey_datetime, program_name):
        """[summary]"""
        db_alerts = {"alerts": [], "warnings": []}
        if journey_datetime is not None:
            db_alerts = self.get_journey_alerts(journey_datetime, program_name)
        elif program_name not in [None, "", "None"]:
            db_alerts = self.get_program_alerts(program_name)
        else:
            # Alerts/Warning from everything
            db_alerts["alerts"] = Alert.objects().order_by("-start_datetime")
            db_alerts["warnings"] = Warn.objects().order_by("-start_datetime")
        return db_alerts

    def is_empty_db_alerts(self, db_alerts, program_name, journey_datetime):
        """[summary]
        """
        if db_alerts["alerts"] is [] and db_alerts["warnings"] is []:
            if program_name in ["current", "previous"] or journey_datetime in ["current", "previous"]:
                return True
        return False

    def update_alert_dict(self, alert_dict, db_alerts):
        """Parse alert/warning querysets to a list of dicts
        """
        for key in alert_dict.keys():
            if db_alerts[key] is not []:
                alert_dict[key] = json.loads(db_alerts[key].to_json()) 
            else:
                alert_dict[key] = []
        return alert_dict
    
    def get_journey_alerts(self, journey_datetime, program_name):
        db_alerts = {"alerts": [], "warnings": []}
        if program_name not in [None, "", "None"]:
            # Alerts/Warning from program and journey
            db_alerts["alerts"] = Alert.objects(
                journey_datetime=journey_datetime, program_name=str(program_name)).order_by("-start_datetime")
            db_alerts["warnings"] = Warn.objects(
                journey_datetime=journey_datetime, program_name=str(program_name)).order_by("-start_datetime")
        else:
            # Alerts/Warning from journey 
            db_alerts["alerts"] = Alert.objects(
                journey_datetime=journey_datetime).order_by("-start_datetime")
            db_alerts["warnings"]  = Warn.objects(
                journey_datetime=journey_datetime).order_by("-start_datetime")
        return db_alerts

    def get_program_alerts(self, program_name):
        """Alerts/Warning from program by name, on current journey
        """
        db_alerts = {"alerts": [], "warnings": []}
        db_alerts["alerts"] = Alert.objects(
            program_name=str(program_name)).order_by("-start_datetime")
        db_alerts["warnings"]  = Warn.objects(
            program_name=str(program_name)).order_by("-start_datetime")
        return db_alerts
    
    def get_alert_warning_number_list(self, journey_datetime=None, program_name=None):
        """Gets the counts of alerts and warnings as a dict
        """
        self.check_db()
        alert_number_dict = {}
        (journey_datetime, program_name) = self.program_manager.check_journey_and_program(journey_datetime, program_name)
        db_alerts = {"alerts": [], "warnings": []}
        try:
            db_alerts = self.get_db_alerts(journey_datetime, program_name)
            if self.is_empty_db_alerts(db_alerts, journey_datetime, program_name):
                return {}
            else:
                alert_number_dict["alert_number"] = len(db_alerts["alerts"])
                alert_number_dict["warning_number"] = len(db_alerts["warnings"])
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return alert_number_dict

    def get_alert_warning_list_by_datetime(self, init_datetime=None, end_datetime=None):
        """Gets a list of alerts and warnings from MongoDB in a specific range of dates
        
        :param init_datetime: Initial datetime for searching alerts, defaults to None
        :type init_datetime: datetime.datetime, optional
        :param end_datetime: Final datetime for searching alerts, defaults to None
        :type end_datetime:  datetime.datetime, optional
        :return: A list of db_models.Alert and db.models.Warning objects from MongoDB 
        :rtype: list
        """
        try:
            self.check_db()
            alert_dict = {}
            alerts_db = Alert.objects(
                start_datetime__gte=init_datetime,
                start_datetime__lte=end_datetime).order_by("-start_datetime")
            warnings_db = Warn.objects(
                start_datetime__gte=init_datetime,
                start_datetime__lte=end_datetime).order_by("-start_datetime")
            alert_dict["alerts"] = json.loads(alerts_db.to_json())
            alert_dict["warnings"] = json.loads(warnings_db.to_json())
            return alert_dict
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
    
    def add_alerts_to_program(self, journey_datetime=None, program=None):
        """Adds alerts to a program object
        :rtype: 
        """
        alert_list = self.get_alert_warning_list(
                    journey_datetime=journey_datetime,
                    program_name=program["program_name"])
        program["alerts"] = alert_list["alerts"]
        program["alert_number"] = len(alert_list["alerts"])
        program["warnings"] = alert_list["warnings"]
        program["warning_number"] = len(alert_list["warnings"])
        return program
    
    def check_anomaly_results(self, timestamp, anomaly):
        self.anomaly_manager.check_anomaly_results(timestamp, anomaly)
