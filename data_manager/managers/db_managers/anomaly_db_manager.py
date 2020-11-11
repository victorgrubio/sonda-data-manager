
NO_DISTORTION = "no_distortion"
from managers.db_managers import BaseDbManager
from helper import config as cfg
from helper import global_variables as gv
from db_models import Alert, Warn, StatusData, Journey, Program, VideoAnalysis
from datetime import datetime

class AnomalyDbManager(BaseDbManager):
    """Class that represents the handler object use to manage anonalies

    :param db_connection: DbConnection instance to handle MongoDb connection
    :type db_connection: data_manager.managers.DbConnection
    :param program_manager: MongoDb handler that manages programs
    :type program_manager: data_manager.managers.db_managers.ProgramDbManager
    """
    
    def __init__(self, db_connection, program_manager):
        """Constructor
        """
        BaseDbManager.__init__(self, db_connection)
        self.program_manager = program_manager

    def check_anomaly_results(self, timestamp_ms, anomaly):
        """Check the results of the anomaly analysis to add any alert
        """
        alert_type = ""
        for index, score in enumerate(anomaly.scores):
            alert_type = self.get_anomaly_event_type_by_score(score)
            gv.logger.info(score)
            if alert_type is not NO_DISTORTION:
                anomaly_data = {
                    "index": index,
                    "timestamp_ms": timestamp_ms,
                    "alert_type": alert_type,
                    "anomaly": anomaly
                }
                self.add_new_distortion_alert_to_db(anomaly_data)

    def get_anomaly_event_type_by_score(self, score):
        if score < cfg.warning_anomaly_threshold:
            return NO_DISTORTION
        if cfg.warning_anomaly_threshold < score < cfg.alert_anomaly_threshold:
            return "warning"
        return "alert"

    def add_new_distortion_alert_to_db(self, anomaly_data):
        anomaly_alert_dict = self.create_new_distortion_event(anomaly_data)
        self.save_new_distortion_alert_in_db(anomaly_alert_dict, anomaly_data["alert_type"])

    def create_new_distortion_event(self, anomaly_data):
        last_document = VideoAnalysis.objects.order_by('-id').first()
        current_program = Program.objects.order_by('-id').first()
        (journey_datetime, program_name) = self.program_manager.check_journey_and_program(journey_datetime=None, program_name="current")
        anomaly_confidence_score = int(anomaly_data["anomaly"].scores[anomaly_data["index"]]*100)
        alert_init_sample_frame = self.get_alert_init_sample_frame(anomaly_data, last_document)
        anomaly_alert_dict = {
            "journey_datetime": journey_datetime,
            "program_name": program_name,
            "document_id": last_document.id,
            "description": "Distortion related to information loss",
            "start_datetime": datetime.fromtimestamp(anomaly_data["timestamp_ms"]//1000),
            "init_sample_frame": alert_init_sample_frame,
            "duration": anomaly_data["anomaly"].window_size,
            "category": "distortion",
            "confidence": anomaly_confidence_score
        }
        if current_program.content_type == "vod":
            anomaly_alert_dict.update({"video_second": last_document.video_second})
        return anomaly_alert_dict

    def get_alert_init_sample_frame(self, anomaly_data, last_document):
        pts_rate = 90000 // last_document.videoSettings.frame_rate
        anomaly_window_init_pts = self.get_anomaly_init_pts(anomaly_data, pts_rate)
        alert_init_frame_sample = ( anomaly_window_init_pts - anomaly_data["anomaly"].init_pts ) // pts_rate
        return alert_init_frame_sample

    def get_anomaly_init_pts(self, anomaly_data, pts_rate):
        # window_step  = window_size - window_overlap
        window_step = anomaly_data["anomaly"].window_size - anomaly_data["anomaly"].window_overlap
        # PTS init of window = anomalyInitPTS(analysis) + indexOfWindow*PTS_RATE*WindowStep
        return anomaly_data["anomaly"].init_pts + anomaly_data["index"]*pts_rate*window_step

    def save_new_distortion_alert_in_db(self, anomaly_alert_dict, alert_type):
        new_distortion_db = None
        if alert_type == "warning":
            anomaly_alert_dict.update({
                "url": "images/alert_video.png"
            })
            new_distortion_db = Alert(**anomaly_alert_dict)
        else:
            anomaly_alert_dict.update({
                "url": "images/alert_video.png"
            })
            new_distortion_db = Warn(**anomaly_alert_dict)
        
        gv.logger.warn(f"New distortion {alert_type} added")
        new_distortion_db.save()
