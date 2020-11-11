import psutil
import signal
import subprocess
import time
from os import kill, getenv
from db_models import StatusData

from helper import config as cfg
from helper import global_variables as gv

class MemoryEmergencyManager:

    @classmethod
    def check_if_process_running(self, process_name):
        """ Check if there is any running process that contains the given name processName.
        
        :param process_name: Name of process to search
        :type process_name: str
        :return: True if process is running an available, else False
        :rtype: boolean
        """
        #Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    @classmethod
    def kill_process_by_name(self, process_name):
        """ Kill a process with a given name
        
        :param process_name: Name of process to kill
        :type process_name: str
        :raises AttributeError: Process is not accessible to be killed
        """
        #Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() in proc.name().lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                raise AttributeError("An error has ocurred while trying to kill process {}: {}".format(process_name, e))
    
    def on_terminate(self, proc):
        gv.logger.warn("process {} terminated with exit code {}".format(proc, proc.returncode))

    @classmethod
    def kill_videoqualityprobe(self, process_pid):
        parent_process = psutil.Process(pid = process_pid)
        procs = parent_process.children()
        for p in procs:
            p.terminate()
        gone, alive = psutil.wait_procs(procs, timeout=3, callback=self.on_terminate)
        for p in alive:
            p.kill()
        parent_process.kill()
        parent_process.wait()
        
    @classmethod
    def check_memory_status(self):
        """Checks if memory consumed by videoqualityprobe is lower than a threshold defined in config

        raises psutil.NoSuchProcess: Process does not exist
        """
        try:
            MB_BYTES = 1048576
            current_status = StatusData.objects.order_by('-id').first()
            videoqualityprobe_process = psutil.Process(current_status.probe_pid)
            probe_memory_consumed_mb = float(videoqualityprobe_process.memory_info().rss) / MB_BYTES
            if current_status.content_type == "live":
                self.check_probe_process_memory_usage(current_status, probe_memory_consumed_mb)
        except psutil.NoSuchProcess as e:
            gv.logger.error(e)

    @classmethod
    def check_probe_process_memory_usage(self, current_status, probe_memory_consumed_mb):
        # If it is consuming too many resources, restarts it
        # Status will not change at all
        if current_status.content_type != "playlist":
            if psutil.pid_exists(current_status.probe_pid) and probe_memory_consumed_mb > cfg.rss_threshold_mb:
                gv.logger.warning("Videomos probe exceeded memory limitation")
                self.kill_videoqualityprobe(current_status.probe_pid)
                # Sleeps while the process is alive
                while(psutil.pid_exists(current_status.probe_pid)):
                    time.sleep(0.1)
                gv.logger.warning("Previous probe has been removed")
                command = [
                    "{}/videoqualityprobe_{}/Release/videoqualityprobe".format(
                        cfg.base_project_path, "live"),
                    "-i", current_status.url,
                    "-x", current_status.mode,
                    "-s", cfg.probe_measure_seconds,
                    "-n", cfg.probe_samples,
                    "-u", "http://localhost:{}".format(getenv("API_PORT"))
                ]
                # Check if there is a program number in config
                if gv.api_dm.db_manager.config_manager.config.program_number:
                    command += ["-p", str(gv.api_dm.db_manager.config_manager.config.program_number)]
                gv.logger.warning("Configuration for restarting\n{}".format(command))
                process = subprocess.Popen(command)
                current_status.update(probe_pid=process.pid)
                current_status.save()
                gv.logger.info("SAVING STATUS DATA")
                current_status.reload()
                gv.logger.warning("Videomos probe has been restarted successfully")