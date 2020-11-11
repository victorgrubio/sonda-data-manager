'''
Created on 16 mar. 2020

@author: victor
'''
from mongoengine import DoesNotExist, MultipleObjectsReturned
import json
import pytz
import time
import traceback
from datetime import datetime, timedelta, timezone
from collections import OrderedDict
from pyrfc3339 import parse, generate
from bson.objectid import ObjectId
from gevent.lock import BoundedSemaphore
from dateutil.tz import tzlocal

from managers.db_managers import BaseDbManager, MosCalculator
from helper import global_variables as gv
from helper import config as cfg
from db_models import Journey, Program, StatusData


class ProgramDbManager(BaseDbManager):
    """Class that represents the handler object use to manage Journeys in MongoDB
    :param db_connection: DbConnection instance to handle MongoDb connection
    :type db_connection: data_manager.managers.DbConnection
    :param config_manager: MongoDb handler that manages config
    :type config_manager: data_manager.managers.db_managers.ConfigDbManager
    :param journey_manager: MongoDb handler that manages journeys
    :type journey_manager: data_manager.managers.db_managers.JourneyDbManager
    :param epg_manager: MongoDb handler that manages epgs
    :type journey_manager: data_manager.managers.EpgManager
    """
    
    def __init__(self, db_connection, config_manager, journey_manager, epg_manager):
        """Constructor
        """
        BaseDbManager.__init__(self, db_connection)
        self.current_program_name_lock = BoundedSemaphore(1)
        self.current_program_name = None
        self.config_manager = config_manager
        self.journey_manager = journey_manager
        self.epg_manager = epg_manager
        self.mos_calculator = MosCalculator(self.config_manager)
        

    @property
    def current_program_name(self):
        value = ""
        self.current_program_name_lock.acquire()
        try:
            self.check_db()
            current_status = StatusData.objects.order_by('-id').first()
            value = current_status.current_program_name
        finally:
            self.current_program_name_lock.release()
        return value

    @current_program_name.setter
    def current_program_name(self, value):
        self.current_program_name_lock.acquire()
        try:
            self.check_db()
            current_status = StatusData.objects.order_by('-id').first()
            if current_status is not None:
                current_status.update(current_program_name=value)
                current_status.reload()
                current_status.save()
            self._current_program_name = value
        finally:
            self.current_program_name_lock.release()

    def update_program_in_db(self, videoanalysis_document, program):
        """Updates program data with a new analysis document
        
        :param document: db_models.VideoAnalysis as dict from the last quality measure.
        :type document: dict
        :param program: Specific program to be updated with a new document
        :type program: db_models.Program
        """
        program = self.update_program_data(videoanalysis_document, program)
        program.reload()
        program.save()

    def update_program_data(self, videoanalysis_document, program):
        new_data = self.get_new_program_data_element(videoanalysis_document)
        # update mos and percentages value
        new_mos = self.mos_calculator.calculate_average_mos_db_object(
            program, videoanalysis_document.mosAnalysis.mos)
        new_percentages = self.mos_calculator.calculate_mos_categories_db_object(
            program, videoanalysis_document.mosAnalysis.mos)        
        program_data = program.data
        program_data.append(new_data)
        # Check if settings have changed
        program_video_settings = self.check_program_video_settings(videoanalysis_document, program)
        program.update(
                mos=new_mos, mos_percentages=new_percentages,
                data=program_data, video_settings=program_video_settings)
        return  program

    def get_new_program_data_element(self, videoanalysis_document):
        new_data = {
            "timestamp": videoanalysis_document.timestamp,
            "mos": videoanalysis_document.mosAnalysis.mos,
            "pts": videoanalysis_document.videoSettings.pts
        }
        # If it is a vod program, we need the videoSecond to draw it
        if videoanalysis_document.videoSettings.video_second is not None:
            new_data.update({
                "videoSettings": {
                    "video_second": videoanalysis_document.videoSettings.video_second
                }
            })
        return new_data

    def check_program_video_settings(self, videoanalysis_document, program):
        """Checks if program video settings have varied with regard to the document provided
        
        :param document: db_models.VideoAnalysis document for current analysis.
        :type document: db_models.VideoAnalysis
        :param program: Program to compare the document with
        :type program: db_models.Program
        :return: Program video settings updated
        :rtype: db_models.VideoSettingsDocument
        """
        program_video_settings = program.video_settings
        document_video_settings = videoanalysis_document.videoSettings
        for setting in program_video_settings:
            # resolution = width x height frame_rate
            if setting == "resolution":
                if program_video_settings[setting] != "{} x {} {}".format(
                    document_video_settings.width,
                    document_video_settings.height,
                    document_video_settings.frame_rate
                ):
                    program_video_settings["resolution"] = "various"
            else:
                if setting == "color_space":
                    continue
                elif document_video_settings[setting] != program_video_settings[setting]:
                    program_video_settings[setting] = "various"
        return program_video_settings

        
    def add_new_program(self, document):
        """Introduces a new document into the Program collection using the last analysis document.
        
        :param document: Last db_models.VideoAnalysis as dict
        :type document: dict
        """
        self.check_db()
        program_name = self.check_current_program_name()
        new_program_dict = self.get_new_program_dict(document, program_name)
        new_program_dict = self.update_program_duration(new_program_dict)
        _ = self.db_connection.db.program.create_index([ ("journey_datetime", -1), ("program_name", -1) ])
        Program(**new_program_dict).save()

    def get_new_program_dict(self, document, program_name):
        current_status = StatusData.objects.order_by('-id').first()
        return {
            "program_name": program_name,
            "journey_datetime": self.journey_manager.journey_datetime,
            "mos": document.mosAnalysis.mos,
            "mos_percentages": self.mos_calculator.get_initial_mos_categories(document),
            "url": current_status.url,
            "content_type": current_status.content_type if current_status is not None else "live",
            "data": [
                self.get_new_program_data_element(document)
            ],
            "video_settings": {
                "color_space": "RGB",
                "pix_format": document.videoSettings.pix_format,
                "scan_type": document.videoSettings.scan_type,
                "codec": document.videoSettings.codec,
                "resolution": "{} x {} {}".format(
                    document.videoSettings.width,
                    document.videoSettings.height,
                    document.videoSettings.frame_rate)
            }
        }

    def update_program_duration(self, new_program_dict):
        current_epg_program = self.epg_manager.get_epg_program_by_time(datetime.now(tzlocal()))
        if current_epg_program is None: # if we don't have epg, duration is based on config
            new_program_dict.update({
                "start_datetime": datetime.now(pytz.utc),
                "end_datetime": datetime.now(pytz.utc) + timedelta(minutes=self.config_manager.config.program_duration),
                "duration": self.config_manager.config.program_duration
            })
        else: # if we have epg, duration is based on EPG
            timedelta_duration = current_epg_program.end_datetime - current_epg_program.start_datetime
            new_program_dict.update({
                "start_datetime": current_epg_program.start_datetime,
                "end_datetime": current_epg_program.end_datetime,
                "duration": timedelta_duration.seconds // 60
            })
        return new_program_dict

    
    def check_journey_and_program(self, journey_datetime=None, program_name=None):
        """Checks the datetime of journey to handle "current" and "previous" 
        
        :param journey_datetime: Unformated journey datetime, defaults to None
        :type journey_datetime: str or datetime.datetime, optional
        :param program_name:  Name of program to check, defaults to None
        :type program_name: str, optional
        :return: journey datetime and program name parsed as tuple
        :rtype: tuple
        """
        if journey_datetime is None:
            # If we only have program, we have to know the journey datetime
            if program_name == "current":
                journey_datetime = self.journey_manager.journey_datetime
            elif program_name == "previous":
                journey_datetime = Program.objects.order_by("-start_datetime")[1].journey_datetime
        else:
            journey_datetime = self.journey_manager.check_journey(journey_datetime=journey_datetime)
        program_name = self.check_program_name(program_name=program_name)
        return (journey_datetime, program_name)

    def check_program_name(self, program_name=None):
        """Checks the program name provide to parse "current" or "previous" strings to a valid program name.
        
        :param program_name: Program name before parsing, defaults to None
        :type program_name: str, optional
        :return: Program name parsed
        :rtype: str
        """
        try:
            if program_name == "current":
                program_name = self.check_current_program_name()
                self.update_current_program_name(program_name)
            elif program_name == "previous":
                program_name = Program.objects.order_by("-start_datetime")[1].program_name
        except IndexError:
            return None
        return  program_name
    
    def check_current_program_name(self):
        """Checks the current program name. Manages the updating of the program_name.
        
        :return: Name of current program
        :rtype: str
        """
        program_name = ""
        try:
            program_name = self.get_current_program_name()
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return program_name

    def get_current_program_name(self):
        current_status = StatusData.objects.order_by('-id').first()
        program_name = self.get_program_name_by_content_type(current_status.content_type)
        if self.current_program_name != program_name:
            self.current_program_name = program_name
        return program_name
    
    def get_program_name_by_content_type(self, content_type):
        if content_type == "live":
            return self.get_live_program_name()
        if content_type == "vod":
            return "1"
        if content_type == "playlist":
            return self.current_program_name

    def get_live_program_name(self):
        current_time = datetime.now(tzlocal())
        current_epg_program = self.get_current_epg_program(current_time)
        time_difference = self.update_journey_time_difference(current_time)
        if current_epg_program is None:
            program_name = self.get_program_name_by_time(time_difference)
        else:
            program_name = current_epg_program.program_name
        return program_name

    def get_current_epg_program(self, current_time):
        current_epg_program = None
        if self.epg_manager.channel != "None": # Default channel defined as "None" string
            current_epg_program = self.epg_manager.get_epg_program_by_time(current_time)
        return current_epg_program

    def update_journey_time_difference(self, current_time):
        time_difference = current_time - self.journey_manager.journey_datetime
        # if length of journey  > journey duration -> create new journey
        if time_difference > timedelta(minutes=self.config_manager.config.journey_duration):
            # If journey duration < 24h and journey_duration is over
            if self.config_manager.config.journey_duration < 60*24:
                gv.api_dm.probe_router.kill_probe_process()
            else:
                self.journey_manager.set_journey_datetime()
                time_difference = 0.0
        return time_difference

    def get_program_name_by_time(self, time_difference):
        journey_current_minutes_played = int(time_difference.total_seconds()/60)
        program_name_by_duration = int(
            journey_current_minutes_played/self.config_manager.config.program_duration
        ) + 1
        return str(max( 1, program_name_by_duration)) # Avoid returning 0

    def update_current_program_name(self, program_name):
        if program_name != self.current_program_name:
            gv.logger.info("Setting new program name")
            self.current_program_name = program_name

    def get_program(self, program_name="current", journey_datetime=None):
        """Gets the program from the db with specific name and journey datetime.
        
        :param program_name: Name of program to get data, defaults to "current"
        :type program_name: str, optional
        :param journey_datetime: Datetime to get the program data, defaults to None
        :type journey_datetime: datetime.datetime, optional
        :raises AttributeError: Program not found in DB
        :return: Program from db with the specific journey_datetime and program name.
        :rtype: db_models.Program
        """
        program = None
        try:
            program = self.get_program_by_name_journey(program_name, journey_datetime)
        except DoesNotExist:
            if program_name in ["current", "previous"]:
                return {}
            else:
                raise AttributeError("Program {} Not Found in DB Manager".format(program_name))
        except MultipleObjectsReturned:
            latest_program = Program.objects.order_by('-id').first()
            latest_program.delete()
            gv.logger.info("Multiple programs, removing corrupted data from import")
        except IndexError:
            gv.logger.info("Previous program not created yet")
            return {}
        return program

    def get_program_by_name_journey(self, program_name, journey_datetime):
        program = None
        if program_name == "current":
            program = Program.objects(program_name=self.current_program_name, journey_datetime=self.journey_manager.journey_datetime).get()
        elif program_name == "previous":
            self.db_connection.db.program.create_index([("start_datetime", -1)])
            program = Program.objects().order_by("-start_datetime")[1]
        else:
            (journey_datetime, program_name) = self.check_journey_and_program(journey_datetime, program_name)
            program = Program.objects(program_name=program_name, journey_datetime=journey_datetime).get()
        return program
    
    
    def get_processed_program(self, journey_datetime=None, program_name=None):
        """Gets a complete program for historic and journey search

        :param journey_datetime: Journey datetime for program, defaults to None
        :type journey_datetime: datetime.datetime or str, optional
        :param program_name: Name of program to search, defaults to None
        :type program_name: str, optional
        :raises AttributeError: Program not found with specific name and journey_datetime
        :return: Program db object with the specific paramenters, as dict
        :rtype: dict
        """
        program_dict = None
        (journey_datetime, program_name) = self.check_journey_and_program(
            journey_datetime=journey_datetime, program_name=program_name)
        try:
            program = Program.objects(journey_datetime=journey_datetime, program_name=program_name).get()
            program_dict = json.loads(program.to_json())
            program_dict = gv.api_dm.db_manager.alert_manager.add_alerts_to_program(journey_datetime, program_dict) 
        except DoesNotExist as e:
            raise AttributeError("Program {} from journey {} Not Found".format(program_name, journey_datetime))
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return program_dict

    
    
    