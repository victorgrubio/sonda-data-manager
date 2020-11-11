import subprocess
import traceback 
import psutil
import time
from gevent.lock import BoundedSemaphore
from helper import global_variables as gv
from helper import config as cfg
from helper import utils
from db_models import StatusData
import routers
from managers.thread_playlist import PlaylistPlayer
from managers.db_connection import DbConnection
from managers.db_managers.mongodb_manager import MongoDbManager
from managers.probe_healthchecker import ProbeHealthChecker
from managers import VideoQualityPredManager


class DataManagerAPI:
    """
    This class represents the DataManager's API Server Manager
    It contains the MongoDB Managing module named as dbManager in addition to
    the different routers for each type of blueprint

    :param db_manager: MongoDB manager, defaults to None
    :type db_manager: managers.db_managers.mongodb_manager, optional
    :param db_router: router in charge of handling DataManager API Db Blueprint methods, defaults to None
    :type db_router: routers.DbRouter, optional
    :param file_router: router in charge of handling DataManager API File Blueprint methods, defaults to None
    :type file_router: routers.FileRouter, optional
    :param probe_router: router in charge of handling DataManager API Probe Blueprint methods, defaults to None
    :type probe_router: routers.ProbeRouter, optional
    :param alert_router: router in charge of handling DataManager API Alert Blueprint methods, defaults to None
    :type alert_router: routers.AlertRouter, optional
    :param journey_router: router in charge of handling DataManager API Journey Blueprint methods, defaults to None
    :type journey_router: routers.JourneyRouter, optional
    :param program_router: router in charge of handling DataManager API Program Blueprint methods, defaults to None
    :type program_router: routers.ProgramRouter, optional
    :param historic_router: router in charge of handling DataManager API Historic Blueprint methods, defaults to None
    :type historic_router: routers.HistoricRouter, optional
    :param document_router: router in charge of handling DataManager API Document Blueprint methods, defaults to None
    :type document_router: routers.DocumentRouter, optional
    """
    def __init__(self, db_manager=None, db_router=None, file_router=None,
                probe_router=None, alert_router=None, journey_router=None,
                program_router=None, historic_router=None, document_router=None):
        """Constructor        
        """
        self.db_manager = MongoDbManager(DbConnection())
        self.videoqualitypred_manager = VideoQualityPredManager()
        self.db_router = routers.DbRouter()
        self.file_router = routers.FileRouter()
        self.config_router = routers.ConfigRouter(self.db_manager.config_manager)
        self.probe_router = routers.ProbeRouter(self.db_manager.config_manager)
        self.alert_router = routers.AlertRouter(self.db_manager.alert_manager)
        self.journey_router = routers.JourneyRouter(self.db_manager.journey_manager)
        self.program_router = routers.ProgramRouter(self.db_manager.program_manager)
        self.historic_router = routers.HistoricRouter(self.db_manager.historic_manager,
                                                    self.db_manager.journey_manager,
                                                    self.db_manager.alert_manager,
                                                    self.db_manager.mos_calculator)
        self.document_router = routers.DocumentRouter(self.db_manager.document_manager,
                                                     self.videoqualitypred_manager)
        self.probe_healthchecker = ProbeHealthChecker()
        self.probe_healthchecker.start()
        self.probe_status_lock = BoundedSemaphore(1)
        self.last_document_time_lock = BoundedSemaphore(1)

    @property
    def probe_status(self):
        """Probe status getter
        Possible values:
            stopped = Default value. It is set after probe is stopped.
            idle = Intermediate status between running and stopped. It happens after probe is launched but it hasn´t processed anything yet.
            running = Probe is processing information.
            killed = Special mode to terminate a playlist.
        
        :return: Current status of the Video Quality Probe
        :rtype: str
        """
        value = ""
        self.probe_status_lock.acquire()
        try:
            status_data = StatusData.objects.order_by('-id').first()
            if status_data is None:
                value = "stopped"
            # Case where VOD stops running
            elif self.is_vod_stopped(status_data):
                value = "stopped"
            else:
                value = status_data.probe_status
        finally:
            self.probe_status_lock.release()
        return value
    
    @probe_status.setter
    def probe_status(self, value):
        """Probe status setter
        
        Possible values:
            stopped = Default value. It is set after probe is stopped.
            idle = Intermediate status between running and stopped. It happens after probe is launched but it hasn´t processed anything yet.
            running = Probe is processing information.
            killed = Special mode to terminate a playlist.
        
        :param value: Current status of Video Quality Probe.
        :type value: str
        """
        self.probe_status_lock.acquire()
        try:
            status_data = StatusData.objects.order_by('-id').first()
            if status_data is None:
                self._probe_status = "stopped"
            else:
                status_data.update(probe_status=value)
                status_data.reload()
                status_data.save()
                self._probe_status = value
        finally:
            self.probe_status_lock.release()

    @property
    def last_document_time(self):
        """Last_document_time attribute getter
        
        :return: timestamp (time module) of last document inserted
        :rtype: float
        """
        value = ""
        self.last_document_time_lock.acquire()
        try:
            status_data = StatusData.objects.order_by('-id').first()
            if status_data is None:
                value = time.time()
            else:
                value = status_data.last_document_time
        finally:
            self.last_document_time_lock.release()
        return value

    @last_document_time.setter
    def last_document_time(self, value):
        """Last_document_time attribute setter
        
        :param value: Time in terms of time module of last document inserted
        :type value: float
        """
        self.last_document_time_lock.acquire()
        try:
            status_data = StatusData.objects.order_by('-id').first()
            if status_data is None:
                self._last_document_time = time.time()
            else:
                status_data.update(last_document_time=value)
                status_data.reload()
                status_data.save()
                self._last_document_time = value
        finally:
            self.last_document_time_lock.release()
    
    def is_vod_stopped(self, status_data):
        if status_data.content_type == "vod":
            if (
                status_data.probe_status == "running" and 
                not psutil.pid_exists(status_data.probe_pid)
            ):
                return True
        return False
            
    
    def update_frame(self):
        """Updates the current frame displayed at website

        API Endpoint: '/videoAnalysis/updateFrame', methods=['GET']
        
        :return: Response
        :rtype: dict
        """
        try:
            command = [
                "cp", "/data/cframe1.jpg",
                "/data/images/cframe1.jpg"
            ]
            _ = subprocess.Popen(command)
            response = utils.build_output(task=cfg.update_frame, status=200,
                                         message=cfg.success_msg, output={})
        except Exception as e:
            gv.logger.error(traceback.format_exc())
            response = utils.build_output(task=cfg.update_frame, status=500,
                                         message=str(e), output={})
        return response
    
    
    

        

    