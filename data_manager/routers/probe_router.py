'''
Created on 17 mar. 2020

@author: victor
'''
import traceback
import subprocess
import json
import signal
import psutil
import pytz
import time 
import signal
from dateutil.tz import tzlocal

from os import kill, getenv
from datetime import datetime

from helper import config as cfg
from helper import global_variables as gv
from db_models import StatusData

from managers.thread_playlist import PlaylistPlayer
from helper import utils
from managers.memory_emergency_manager import MemoryEmergencyManager


class ProbeRouter:
    """A class that represents the router in charge of handling DataManager API Probe Blueprint methods
        
    :param config_manager: DbManager in charge of handling ProbeConfig documents in MongoDB
    :type config_manager: managers.db_managers.ConfigDbManager
    """
    
    def __init__(self, config_manager):
        """Constructor
        """
        self.config_manager = config_manager
        self.journey_datetime = None # Datetime object
        self.content_type = ""
        self.current_status = None # StatusData object
    
    def launch_videoqualityprobe(self):
        """Starts a VideoQualityProbe with the current config
        Stores the PID of the process for future stop
        API Endpoint: '/videoAnalysis/probe/launch', methods=['POST']
    
        """
        self.set_probe_router_attributes()
        self.launch_probe_by_url()
        
    def set_probe_router_attributes(self):
        self.journey_datetime = datetime.now(pytz.UTC).replace(microsecond=0)
        self.current_status = StatusData.objects.order_by('-id').first()
        self.content_type = "vod" if cfg.upload_path in self.config_manager.config.url else "live"
        # If previous execution was live, then insert in previous journey
        if self.current_status is not None:
            if self.current_status.content_type == "live" and self.content_type == "live":
                self.journey_datetime = self.current_status.journey_datetime.replace(tzinfo=pytz.utc).astimezone(pytz.utc)
            self.check_probe_running()

    def check_probe_running(self):
        """
        """
        process_name = ""
        if self.current_status.content_type != "playlist":
            if psutil.pid_exists(self.current_status.probe_pid):
                gv.logger.info(json.loads(self.current_status.to_json()))
                process_name = psutil.Process(self.current_status.probe_pid).name()
            # If there is a probe already, kills it
            if gv.api_dm.probe_status != "stopped" and process_name == "videoqualityprobe":
                if psutil.pid_exists(self.current_status.probe_pid):
                    gv.logger.warning("Current probe has been killed")
                    kill(self.current_status.probe_pid, signal.SIGKILL)
                    gv.api_dm.probe_status = "stopped"
                    time.sleep(1)
                else:
                    pass
    
    def launch_probe_by_url(self):
        if self.config_manager.config.url.endswith(cfg.playlist_extension):
            self.launch_probe_playlist()
        else:
            self.start_probe_process()
        
    def start_probe_process(self):
        process = self.launch_command_probe()
        status_data = self.get_new_probe_status(process.pid)
        status_data.save()
        gv.logger.info("Launched probe with info: {}".format(
            json.loads(status_data.to_json()))
        )
        gv.logger.info("Status after command: {}".format(gv.api_dm.probe_status))

    def get_new_probe_status(self, probe_pid):
        status_data_dict = {
            "url": self.config_manager.config.url,
            "probe_pid": probe_pid,
            "start_datetime": datetime.now(pytz.UTC),
            "mode": str(self.config_manager.config.mode),
            "probe_status": "idle",
            "process_name": psutil.Process(probe_pid).name(),
            "last_document_time": time.time(),
            "journey_datetime": self.journey_datetime,
            "current_program_name": "",
            "content_type": self.content_type
        }
        status_data_dict = self.add_program_number(status_data_dict)
        return StatusData(**status_data_dict)

    def add_program_number(self, status_data_dict):
        if self.config_manager.config.program_number:
            status_data_dict.update({
                "program_number": self.config_manager.config.program_number
            })
        return status_data_dict
    
    def launch_command_probe(self):
        self.current_status = StatusData.objects.order_by('-id').first()
        command = [
            "{}/videoqualityprobe_{}/Release/videoqualityprobe".format(
                cfg.base_project_path, self.content_type),
            "-i", self.config_manager.config.url,
            "-x", str(self.config_manager.config.mode),
            "-s", cfg.probe_measure_seconds
        ]
        if self.content_type != "vod":
            command += ["-n", str(self.config_manager.config.samples)]
        if self.config_manager.config.program_number:
            command += ["-p", str(self.config_manager.config.program_number)]
        command += ["-u", "http://localhost:{}".format(getenv("API_PORT"))]
        if self.is_probe_running():
            gv.logger.warning("Previous probe killed")
            self.kill_probe_process()
        process = subprocess.Popen(command)
        return process

    def is_probe_running(self):
        for proc in psutil.process_iter():
            if cfg.process_name in proc.name().lower():
                return True    
        return False

    def restart_probe(self):
        current_status = StatusData.objects.order_by('-id').first()
        if (current_status.probe_status != "idle"):
            gv.logger.warning("Videoqualityprobe has been killed by an unknown external process")
            gv.logger.warning("Trying to restart it using the current configuration")
            self.set_probe_router_attributes()
            self.launch_probe_by_url()
            gv.logger.warning("Restarted probe")
        else:
            gv.logger.info("Another worker has already restarted the process ...")

    def launch_probe_playlist(self):
        config = self.config_manager.config
        if config.url.endswith(cfg.playlist_extension):
            with open(config.url) as f:
                playlist = f.readlines()
            playlist = [x.strip() for x in playlist] 
            self.playlist_player = PlaylistPlayer(
                playlist=playlist, mode=str(config.mode)
            )
            self.playlist_player.start()
        else:
            raise AttributeError(f"Playlist file extension is wrong. Please upload a {cfg.playlist_extension} file")
        gv.logger.info("Status after command: {}".format(gv.api_dm.probe_status))
        
    def stop_videoqualityprobe(self):
        """Stops the current VideoQualityProbe
        API Endpoint: '/videoAnalysis/probe/stop', methods=['POST']

        :raises AttributeError: PID of the VideoQualityProbe executing
        """
        gv.logger.info("/probe/stop: Probe has been stopped by user")
        self.kill_probe_process()
    
    def kill_probe_process(self):
        self.current_status = StatusData.objects.order_by('-id').first()
        if self.current_status is None:
            raise AttributeError("PID of Videoqualityprobe process not idenfied. Probe has not been started yet.")
        else:
            # Added an special status (killed) to kill playlist process
            if self.current_status.content_type == "playlist":
                gv.api_dm.probe_status = "killed"
            MemoryEmergencyManager.kill_process_by_name("videoqualityprobe")
            time.sleep(0.5)
            gv.api_dm.probe_status = "stopped"
            gv.logger.info("Probe has been stop either by user or due to no more content")
    
    def kill_playlist_process(self):
        self.current_status = StatusData.objects.order_by('-id').first()
        if self.current_status is None:
            raise AttributeError("PID of Videoqualityprobe process not idenfied. Probe has not been started yet.")
        else:
            gv.api_dm.probe_status = "stopped"
            # Kill process
            kill(self.current_status.probe_pid, signal.SIGTERM)
            gv.logger.warning("Playlist probe has been stopped")

    