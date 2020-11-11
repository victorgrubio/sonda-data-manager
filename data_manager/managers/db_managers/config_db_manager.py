'''
Created on 16 mar. 2020

@author: victor
'''
from gevent.lock import BoundedSemaphore
from datetime import datetime, timedelta, timezone
import pytz
import traceback
import json
import subprocess

from managers.db_managers import BaseDbManager
from helper import global_variables as gv
from helper import config as cfg
from db_models import ProbeConfig, StatusData


class ConfigDbManager(BaseDbManager):
    """Class that represents the handler object use to manage Alerts in MongoDB
        
    :param db_connection: DbConnection instance to handle MongoDb connection
    :type db_connection: data_manager.managers.DbConnection
    """
    
    def __init__(self, db_connection):
        """Constructor
        """
        BaseDbManager.__init__(self, db_connection)
        self.config_lock = BoundedSemaphore(1)
        self.config = self.get_config()
        
    @property
    def config(self):
        """Getter for the config attribute
        
        :return: Current config in DB
        :rtype: dict
        """
        value = ""
        self.config_lock.acquire()
        try:
            self.check_db()
            value = self.get_config()
        finally:
            self.config_lock.release()
        return value

    @config.setter
    def config(self, value):
        """Setter for config attribute
        
        :param value: New config
        :type value: dict
        """
        self.config_lock.acquire()
        try:
            self.check_db()
            self._config = value
        finally:
            self.config_lock.release()


    def get_config(self):
        """Gets config from DB. If it does not exist, creates a new one from the default values of db_models.ProbeConfig.
        
        :return: current config in db as dict
        :rtype: dict
        """
        config_db = None
        try:
            self.check_db()
            # return config as Python
            config_db = ProbeConfig.objects.first()
            if config_db is None:
                # If there is no config, creates a default
                config_db = ProbeConfig(**{})
                config_db.save()
        except Exception as e:
            gv.logger.error(e)
        return config_db
    
    def put_config(self, config_option_dict):
        """Sets new config in mongoDB as db_models.ProbeConfig
        
        :param config_option_dict: Config dict for new configuration 
        :type config_option_dict: dict
        """
        try:
            self.check_db()
            # parse dict keys to lowercase
            gv.logger.info(config_option_dict)
            for old_key in config_option_dict.keys():
                config_option_dict[old_key.lower()] = config_option_dict.pop(old_key)
            if ProbeConfig.objects.count() > 0:
                ProbeConfig.objects.delete({})
            if "samples" in config_option_dict.keys():
                del config_option_dict["samples"]
            config = ProbeConfig(**config_option_dict)
            config.save()
            self.config = config
	        # TODO Add auto program filter functionality
        except Exception as e:
            gv.logger.error(e)
