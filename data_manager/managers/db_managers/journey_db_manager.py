'''
Created on 16 mar. 2020

@author: victor
'''
import pytz
import traceback
import time
from dateutil.tz import tzlocal

from pyrfc3339 import parse, generate
from mongoengine import DoesNotExist, MultipleObjectsReturned
from gevent.lock import BoundedSemaphore
from datetime import datetime, timedelta, timezone

from managers.db_managers import BaseDbManager, MosCalculator
from helper import global_variables as gv
from helper import config as cfg
from db_models import Journey, Program, StatusData
from managers.file_manager import file_utils


class JourneyDbManager(BaseDbManager):
    """Class that represents the handler object use to manage Journeys in MongoDB
        
    :param db_connection: DbConnection instance to handle MongoDb connection
    :type db_connection: data_manager.managers.DbConnection
    :param config_manager: MongoDb handler that manages config
    :type config_manager: data_manager.managers.db_managers.ConfigDbManager
    """
    def __init__(self, db_connection, config_manager):
        """Constructor
        """
        BaseDbManager.__init__(self, db_connection)
        self.journey_datetime_lock = BoundedSemaphore(1)
        self.journey_datetime = None
        self.mos_calculator = MosCalculator(config_manager)
        self.config_manager = config_manager
        
    @property
    def journey_datetime(self):
        """Getter for the journey_datetime attribute
        
        :return: Current datetime in DB
        :rtype: datetime.datetime
        """
        value = ""
        self.journey_datetime_lock.acquire()
        try:
            self.check_db()
            current_status = StatusData.objects.order_by('-id').first()
            # Initial status: No journeys and stopped
            if self.get_journeys_date_list() == [] and current_status.probe_status in ["stopped", "idle"]:
                value = datetime.now(tzlocal())
            else:
                value = current_status.journey_datetime.replace(tzinfo=pytz.utc).astimezone(pytz.utc)
        finally:
            self.journey_datetime_lock.release()
        return value

    @journey_datetime.setter
    def journey_datetime(self, value):
        """Setter for journey_datetime value
        
        :param value: New journey datetime attribute
        :type value: datetime.datetime
        """
        self.journey_datetime_lock.acquire()
        try:
            self.check_db()
            current_status = StatusData.objects.order_by('-id').first()
            if current_status is not None and value is not None:
                if self.is_different_journey(value, current_status.journey_datetime):
                    current_status.update(journey_datetime=value)
                    current_status.reload()
                    current_status.save()
                    gv.logger.info("Journey has changed to {}".format(value))
            self._journey_datetime = value
        finally:
            self.journey_datetime_lock.release()
    
    def is_different_journey(self, new_journey, status_journey):
        if new_journey is None:
            return True
        if status_journey.replace(tzinfo=pytz.UTC) != new_journey:
            return True
        return False

    def update_journey_data(self, journey, document):
        """Updates Journey's mos and mos_percentages using the last document measured.
        
        :param journey: Journey to be updated
        :type journey: db_models.Journey
        :param document: VideoAnalysisDocument as dict
        :type document: dict
        :return: Updated Journey
        :rtype: db_models.Journey
        """
        new_mos = self.mos_calculator.calculate_average_mos_db_object(journey, document.mosAnalysis.mos)
        new_percentages = self.mos_calculator.calculate_mos_categories_db_object(journey, document.mosAnalysis.mos)
        journey.update(mos=new_mos, mos_percentages=new_percentages, inc__measures=1)
        journey.reload()
        journey.save()
    
    def get_journeys_date_list(self):
        """Gets the list of journey datetimes inside the databse to access them
        
        :return: List of start datetime (as str) for each journey in db.
        :rtype: list of datetimes formatted as string
        """
        journeys_date_list = []
        try:
            journeys = Journey.objects()
            journeys_date_list = [generate(journey.journey_datetime, accept_naive=True) for journey in journeys]
        except DoesNotExist as e:
            gv.logger.warn("No journeys in DB")
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return journeys_date_list

    def get_journey(self, journey_datetime=None):
        """Get the journey object for a given datetime
        
        :param journey_datetime: Journey start datetime, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :raises AttributeError: Journey with datetime provided Not Found
        :return: Journey object from db
        :rtype: db_models.Journey
        """
        journey_datetime = self.check_journey(journey_datetime)
        journey = None
        try:
            self.check_db()
            journey = Journey.objects(journey_datetime=journey_datetime).get()
        except DoesNotExist as e:
            raise AttributeError("Journey {} Not Found".format(journey_datetime))
        except MultipleObjectsReturned as e:
            latest_journey = Journey.objects.order_by('-id').first()
            latest_journey.delete()
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return journey
    
    def get_journey_program_name_list(self, journey_datetime=None):
        """Gets the list of programs from a specific journey
        
        :param journey_datetime: datetime for the journey to list program from, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :raises AttributeError: Journey not found
        :return: List of program names
        :rtype: list of str
        """
        program_name_list = None
        journey_datetime = self.check_journey(journey_datetime=journey_datetime)
        try:
            programs_journey_db = Program.objects(journey_datetime=journey_datetime).order_by('-start_datetime')
            program_name_list = [program.program_name for program in programs_journey_db]
        except DoesNotExist as e:
            raise AttributeError("Programs Journey {} Not Found".format(journey_datetime))
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return program_name_list

    def get_journey_program_list(self, journey_datetime=None):
        """Gets the program objects correspondent to a concrete journey
        
        :param journey_datetime: datetime for the journey to list program from, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :raises AttributeError: Journey not found
        :return: List of programs from db.
        :rtype: List of db_models.Program
        """
        program_list_db = []
        journey_datetime = self.check_journey(journey_datetime=journey_datetime)
        try:
            program_list_db = Program.objects(journey_datetime=journey_datetime)
        except DoesNotExist as e:
            raise AttributeError("Programs Journey {} Not Found".format(journey_datetime))
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return program_list_db

    def check_journey(self, journey_datetime=None):
        """Check with journey is provided from the parameter
        
        :param journey_datetime: ,defaults to None
        :type journey_datetime: str or datetime are valid, optional
        :return: Journey start datetime
        :rtype: datetime.datetime
        """
        try:
            if journey_datetime == "current":
                # If none, sets it
                if self.journey_datetime == None:
                    gv.logger.info("Setting current journey")
                    self.set_journey_datetime()
                journey_datetime = self.journey_datetime
            elif journey_datetime == "previous":
                journey_datetime = Journey.objects.order_by("-journey_datetime")[1].journey_datetime
            elif type(journey_datetime) == str:
                journey_datetime = parse(journey_datetime)
                gv.logger.info("Datetime of search: {}".format(journey_datetime))
        except IndexError:
            return None
        return journey_datetime

    def set_journey_datetime(self):
        """Sets journey datetime if None is provided
        """
        current_status = StatusData.objects.order_by('-id').first()
        journey_datetime = datetime.now(tzlocal())
        if (journey_datetime - datetime.now(tzlocal())).seconds > 0:
            journey_datetime -= timedelta(days=1)
        # if Live, journey_datetime = config
        # TODO: check if previous status was live (equal) or VOD (starts new journey)(more complex)
        if current_status is not None:
            if current_status.content_type == "live":
                journey_datetime = self.get_config_journey_datetime()
            # if VOD, journey_datetime = launch time
            elif current_status.content_type in ["playlist", "vod"]:
                journey_datetime = current_status.journey_datetime.replace(tzinfo=pytz.utc)
        self.journey_datetime = journey_datetime

    def get_config_journey_datetime(self):
        """Gets the journey datetime defined with config parameters
        
        :return: The datetime obtained from config
        :rtype: datetime.datetime
        """
        journey_datetime = datetime.now().replace(
                hour = int(self.config_manager.config.journey_start_time / 60),
                minute = int(self.config_manager.config.journey_start_time % 60),
                second = 0,
                microsecond = 0,
                tzinfo=tzlocal()
        )
        # Check if the config journey corresponds to next day or current  
        return journey_datetime

    def add_new_journey(self, current_status):
        journey = Journey(**{
            "journey_datetime": self.journey_datetime,
            "mos": 0.0,
            "mos_percentages": {
                "mos_poor": 0,
                "mos_regular": 0,
                "mos_good": 0,
                "mos_excellent": 0
                },
            "measures": 0,
            "duration": self.config_manager.config.journey_duration,
            "program_duration": self.config_manager.config.program_duration,
            "content_type": current_status.content_type if current_status is not None else "live"
        })
        # updates the journey datetime of the epg
        gv.api_dm.db_manager.program_manager.epg_manager.current_epg.update(journey_datetime=self.journey_datetime)
        _ = self.db_connection.db.journey.create_index([ ("journey_datetime", -1) ])
        gv.logger.info("Inserted new journey with start {}".format(self.journey_datetime))
        # add journey to db
        journey.save()
        # Remove old files when journey is created
        file_utils.remove_old_files()
        return journey
    
    