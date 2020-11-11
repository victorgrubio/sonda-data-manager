from threading import Thread, Lock, Event
import time
import psutil
import pytz
import subprocess
from datetime import datetime
from os import getenv
from mongoengine import connect
from helper import global_variables as gv
from helper import config as cfg
from db_models import StatusData

class SubprocessWait( object ):
    """Special subprocess class that waits until is finished when executed
        
    :param command_text_list: Command to run as a list 
    :type command_text_list: List of strings
    """
    def __init__( self, command_text_list ):
        """Constructor
        """
        self.command_text_list = command_text_list
    
    def execute(self):
        """Runs the command defined on initialization and wait until it is finished.
        """
        self.process = subprocess.Popen(self.command_text_list)
        self.process.wait()


class PlaylistPlayer:
    """
    This class represents a Playlist mode custom handler.
    This object is able to reproduce consecutive videos from a list of urls. Manages run, start and stop events with threads.
        
    :param playlist: List of videos to reproduce, defaults to []
    :type playlist: list, optional
    :param mode: VideoQualityProbe mode to use in playlist analysis, defaults to "complete"
    :type mode: str, optional
    """

    def __init__(self, playlist=[], mode="complete"):
        """Constructor
        """
        self.playlist = playlist
        self.mode = mode
        self.index = 0
        self.video_command = ""
        self.thread = None
        self.journey_datetime_lock = Lock()
        self.journey_datetime = None
        connect(cfg.db_name, host=cfg.host, port=int(cfg.db_port))

    @property
    def journey_datetime(self):
        """Current journey datetime getter
        
        :return: Current journey datetime
        :rtype: datetime.datetime
        """
        value = ""
        self.journey_datetime_lock.acquire()
        try:
            value = self._journey_datetime
        finally:
            self.journey_datetime_lock.release()
        return value

    @journey_datetime.setter
    def journey_datetime(self, value):
        """Current journey datetime setter
        
        :param value: Current journey datetime
        :type value: datetime.datetime
        """
        self.journey_datetime_lock.acquire()
        try:
            self._journey_datetime = value
        finally:
            self.journey_datetime_lock.release()

    def start(self):
        """
        Starts a thread that calls run method
        """
        gv.logger.info("Started playing new playlist")
        thread = Thread(target=self.run, args=())
        thread.daemon = True
        self.thread = thread
        thread.start()

    def stop(self):
        """Stops thread execution
        """
        self.thread.do_run = False
        self.thread.join()
        gv.logger.info("Playlist has been stopped")

    def run(self):
        """Thread run method
        
        Iterates over each video url executing the Video Quality Probe with specific configurations.
        Waits for each process to be finished before processing next video.
        Stores data in MongoDB.
        """
        for index, playlist_line in enumerate(self.playlist):
            gv.logger.info("New video")
            self.index = index
            self.video_command = playlist_line.strip(" ")
            gv.logger.info(self.video_command)
            if gv.api_dm.probe_status == "killed":
                gv.logger.info("Exiting playlist")
                break
            self.launch_video_process()
            gv.logger.info("Finished video")
        self.finish_playlist()

    def launch_video_process(self):
        if type(self.video_command == str):
            self.video_command = [self.video_command]
        command_text = [
            f"{cfg.base_project_path}/videoqualityprobe_vod/Release/videoqualityprobe",
            "-i" 
            ] + self.video_command + [
            "-x", self.mode,
            "-s", cfg.probe_measure_seconds,
            "-u", "http://localhost:{}".format(getenv("API_PORT"))
            ]
        subprocess_wait = SubprocessWait(command_text)
        self.update_status()
        subprocess_wait.execute()
        gv.logger.info(f"Finished video {self.video_command[0]} ({self.index+1}/{len(self.playlist)})")

    def update_status(self):
        # Journey datetime set by first video
        if self.index == 0:
            self.journey_datetime = datetime.utcnow().replace(microsecond=0)
        status_data = StatusData(**{
            "url": self.video_command[0],
            "start_datetime": datetime.utcnow(),
            "mode": self.mode,
            "probe_status": "idle",
            "last_document_time": time.time(),
            "journey_datetime": self.journey_datetime,
            "current_program_name": str(self.index + 1),
            "content_type": "playlist"
        })
        status_data.save()
        status_data.reload()

    def finish_playlist(self):
        # Set status to stopped
        last_status = StatusData.objects.order_by('-id').first()
        last_status.update(probe_status="stopped")
        last_status.save()
        last_status.reload()
        gv.logger.info("Playlist has finished")
        self.index = 0
        self.video_command = ""