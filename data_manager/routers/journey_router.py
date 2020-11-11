'''
Created on 17 mar. 2020

@author: victor
'''

from helper import global_variables as gv
from helper import utils
import json
import traceback

class JourneyRouter:
    """A class that represents the router in charge of handling DataManager API Journeys Blueprint methods

    :param journey_manager: DbManager in charge of handling Journey documents in MongoDB
    :type journey_manager: managers.db_managers.JourneyDbManager
    """
    
    def __init__(self, journey_manager):
        """Constructor
        """
        self.journey_manager = journey_manager
        
    def get_journeys_date_list(self):
        """Gets the list of dates of journeys in MongoDB
        
        API Endpoint: '/videoAnalysis/journeys/date-list', methods=['GET']
        
        :raises AttributeError: No journey found in DB
        :return: list of journey datetimes as strings
        :rtype: list[str]
        """
        journeys_date_list = []
        try:
            journeys_date_list = self.journey_manager.get_journeys_date_list()
        except AttributeError:
            raise AttributeError("No journey found in DB")
        except Exception as e:
            gv.logger.error(e)
        return journeys_date_list


    def get_journey(self, journey_datetime=None):
        """Gets the data of a complete journey by its datetime

        :param journey_datetime: Datetime of the journey to find, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :raises AttributeError: Journey not found
        :return: The journey data with the datetime provided
        :rtype: datetime.datetime
        """
        journey = {}

        try:
            journey = self.journey_manager.get_journey(journey_datetime=journey_datetime)
        except AttributeError:
            if journey_datetime in ["current", "previous"]:
                return {}
            else:
                raise AttributeError("Journey {} Not Found".format(journey_datetime))
        except Exception as e:
            gv.logger.error(e)
        return journey


    def get_journey_program_name_list(self, journey_datetime=None):
        """Gets the complete list of program names from a concrete journey

        API Endpoint: '/videoAnalysis/journeys/program-name-list', methods=['GET']
        
        :param journey_datetime: Datetime of the journey to find, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :raises AttributeError: Journey not found
        :return: List with names of each program in journey
        :rtype: list[str]
        """
        program_name_list = []

        try:
            program_name_list = self.journey_manager.get_journey_program_name_list(journey_datetime=journey_datetime)
        except AttributeError:
            raise AttributeError("Journey {} Not Found".format(journey_datetime))
        except Exception as e:
            gv.logger.error(e)
        return program_name_list


    def get_journey_program_list(self, journey_datetime=None):
        """Gets the data of each program from an specific list

        API Endpoint: '/videoAnalysis/journeys/program-list', methods=['GET']
        
        :param journey_datetime: Datetime of the journey to find, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :raises AttributeError: Journey not found
        :return: List of programs from a journey
        :rtype: List[db_models.Program]
        """
        program_list = []

        try:
            program_list = json.loads(self.journey_manager.get_journey_program_list(journey_datetime=journey_datetime).to_json())
            for program in program_list:
                alert_list = gv.api_dm.alert_router.get_alert_warning_list(journey_datetime=journey_datetime, program_name=program["program_name"])
                program.update(alert_list)
        except AttributeError:
            raise AttributeError("Journey {} Not Found".format(journey_datetime))
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return program_list