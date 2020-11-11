import psutil
import time
from mongoengine import connect
from threading import Thread
from helper import global_variables as gv
from helper import config as cfg
from db_models import StatusData


class ProbeHealthChecker:
    """[summary]
    """

    def __init__(self):
        """Constructor
        """
        self.thread = None
        connect(cfg.db_name, host=cfg.host, port=int(cfg.db_port))
        
    def start(self):
        """
        Starts a thread that calls run method
        """
        gv.logger.info("Videoqualityprobe healthcheck thread started")
        thread = Thread(target=self.run, args=())
        thread.daemon = True
        self.thread = thread
        thread.start()

    def run(self):
        """Thread run method
        """
        while gv.api_dm is None:
            time.sleep(1)
        while True:
            # Only checks health if 
            self.check_probe_health()
            time.sleep(cfg.healthcheck_interval)

    def check_probe_health(self):
        current_status = StatusData.objects.order_by('-id').first()
        if gv.api_dm.probe_status not in ["stopped", "idle"] and current_status.content_type != "playlist":
            if(psutil.pid_exists(current_status.probe_pid)):
                return
            else:
                # If VideoQP has been killed, restarts it
                gv.logger.warning("Something went wrong ... restarting the probe")
                gv.api_dm.probe_router.set_probe_router_attributes()
                gv.api_dm.probe_router.launch_probe_by_url()
        else:
            return