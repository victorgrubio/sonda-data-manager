'''
Created on 17 mar. 2020

@author: victor
'''
import json
import traceback

from helper import global_variables as gv


class AlertRouter:
    """A class that represents the router in charge of handling DataManager API Alerts Blueprint methods
        
    :param alert_manager: DbManager in charge of handling Alert/Warn documents in MongoDB
    :type alert_manager: managers.db_managers.AlertDbManager
    """
    
    def __init__(self, alert_manager):
        """Constructor
        """
        self.alert_manager = alert_manager
    
    def get_alert_warning_list(self, journey_datetime=None, program_name=None):
        """Gets the list of alerts and warnings from a specific journey datetime and program name
        
        :param journey_datetime: Datetime of journey, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :param program_name: Name of program, defaults to None
        :type program_name: str, optional
        :return: lists of alerts and warnings as a dict
        :rtype: dict
        """
        alert_dict = {}

        try:
            alert_dict = self.alert_manager.get_alert_warning_list(journey_datetime=journey_datetime, program_name=str(program_name))
        except Exception as e:
            gv.logger.error(e)
        return alert_dict


    def get_alert_warning_number(self, journey_datetime=None, program_name=None):
        """Gets the number of alerts and warning from a specific journey datetime and program name
        
        :param journey_datetime: Datetime of journey, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :param program_name: Name of program, defaults to None
        :type program_name: str, optional
        :return: Count of alerts and warning produced in the specified journey / program
        :rtype: dict
        """
        alert_number_dict = {}
        try: 
            alert_number_dict = self.alert_manager.get_alert_warning_number_list(journey_datetime=journey_datetime, program_name=str(program_name))
        except Exception as e:
            gv.logger.error(e)
        return alert_number_dict

    
    def check_anomaly_results(self, timestamp, anomaly):
        try:
            self.alert_manager.check_anomaly_results(timestamp, anomaly)
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())