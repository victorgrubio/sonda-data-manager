'''
Created on 17 mar. 2020

@author: victor
'''
import traceback
from helper import global_variables as gv
from helper import utils


class ProgramRouter:
    """A class that represents the router in charge of handling DataManager API Program Blueprint methods

    :param program_manager: DbManager in charge of handling Program documents in MongoDB
    :type program_manager: managers.db_managers.ProgramDbManager
    """
    
    def __init__(self, program_manager):
        """Constructor
        """
        self.program_manager = program_manager
    
    def get_processed_program(self, journey_datetime=None, program_name=None):
        """Gets a processed program with a certain name from a concrete journey
        
        :param journey_datetime: Journey start datetime, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :param program_name: Name of program to obtain, defaults to None
        :type program_name: str, optional
        :raises AttributeError: Program not Found
        :return: Program requested
        :rtype: db_models.Program
        """
        program = None
        try:
            program = self.program_manager.get_processed_program(journey_datetime=journey_datetime, program_name=str(program_name))
        except AttributeError:
            raise AttributeError("Program {} Journey {} Not Found".format(
                program_name, journey_datetime))
        except Exception as e:
            gv.logger.error(f"{type(e)} - {e}")
        return program



    def get_program(self,journey_datetime=None, program_name="current"):
        """Gets a program with a concrete program name from a specific journey
        
        :param journey_datetime: datetime from journey to search, defaults to None
        :type journey_datetime: str/datetime, optional
        :param program_name: Name of program to obtain, defaults to "current"
        :type program_name: str, optional
        :return: Program requested
        :rtype: db_models.Program
        """
        program = None
        try:
            program = self.program_manager.get_program(program_name=str(program_name), journey_datetime=None)
            return program
        except AttributeError:
            raise AttributeError("Program {} Not Found".format(program_name))
        except Exception as e:
            gv.logger.error(f"{type(e)} - {e}")
        return program