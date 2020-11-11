import xmltodict
import pytz
import time
import traceback
from os.path import isfile
from os import getpid
from dateutil.tz import tzlocal
from datetime import datetime, timedelta
from threading import Thread
from mongoengine.errors import NotUniqueError
from mongoengine import DoesNotExist

from helper import global_variables as gv
from helper import config as cfg
from db_models import Epg, EpgProgram, StatusData

class EpgManager:
    """
    Processor for WebGrabPlus XML

        We will use xmltodict to parse the file. It contains a dict with one key and value. 
        Therefore we go to this item and we found 4 keys: 
            - @generator-info-name
            - @generator-info-url
            - channel
            - programme

        Example channel value:
            OrderedDict([('@id', 'La 1'), ('display-name', OrderedDict([('@lang', 'es'), ('#text', 'La 1')])), ('url', 'http://www.formulatv.com')])

        Example program value:
            OrderedDict([('@start', '20200508161500 +0200'), ('@stop', '20200508163000 +0200'), ('@channel', 'La 1'), ('title', OrderedDict([('@lang', 'es'), ('#text', 'El tiempo')]))])
    """
    def __init__(self, db_connection, config_manager, journey_manager, guide_file=None, channel=None):
        self.db_connection = db_connection
        self.config_manager = config_manager
        self.journey_manager = journey_manager
        self.guide_file = guide_file # Stores only the filename of our guide file
        self.guide_data = guide_file # Using custom setter, we obtain the data from the file using xmldict
        self.guide_data_dict = list(self.guide_data.values())[0]
        self.date_parsing_string = '%Y%m%d%H%M%S %z'
        self.current_epg = None
        self.channel = "None"
        self.channels = None 
        self.programs = []
        self.guide_file_check_thread = None # Thread to check if the guide file has changed
        self.start_guide_file_checker_thread()
        self.create_indexes()
        self.is_epg_generating = False

    @property
    def guide_data(self):
        return self.__guide_data

    @guide_data.setter
    def guide_data(self, guide_file):
        try:
            if guide_file is not None and isfile(guide_file):
                with open(guide_file, encoding="utf-8") as fd:
                    self.__guide_data = xmltodict.parse(fd.read())
            else: 
                self.__guide_data = None
        except Exception as e:
            self.__guide_data = None
            gv.logger.error(e)

    @property
    def channel(self):
        return self.config_manager.config.epg_channel_name

    @channel.setter
    def channel(self, value):
        try:
            self.__channel = value
        except Exception as e:
            gv.logger.error(e)
    
    @property
    def current_epg(self):
        # We could have two epgs for the same journey 
        # due to mismatch in journey beginning and guide_data generation
        # Therefore, we get the most recent of the possible two
        try:
            return Epg.objects().order_by('-id').first()
        except DoesNotExist:
            return None

    @current_epg.setter
    def current_epg(self, new_epg):
        try:
            self.__current_epg = new_epg
        except Exception as e:
            gv.logger.error(e)

    @property
    def programs(self):
        if self.current_epg is not None:
            return self.current_epg.programs
        return []

    @programs.setter
    def programs(self, new_programs):
        try:
            self.__programs = new_programs
        except Exception as e:
            gv.logger.error(e)

    @property
    def channels(self):
        try:
            return self.get_guide_data_channels()
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
    
    @channels.setter
    def channels(self, new_channels):
        try:
            self.__channels = new_channels
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())

    def create_indexes(self):
        # We create indexes to access programs by channels and channels faster
        _ = self.db_connection.db.epg.create_index([("channels", -1)])
        _ = self.db_connection.db.epg.create_index([("epg_program", -1)])
        _ = self.db_connection.db.epg.create_index([("epg_program.channel", -1)])
    
    def get_epg_program_by_time(self, datetime):
        channel_programs = self.current_epg.programs.filter(channel=self.channel)
        for program in channel_programs:
            program_start_datetime_tzaware = program.start_datetime.replace(tzinfo=pytz.UTC)
            program_end_datetime_tzaware = program.end_datetime.replace(tzinfo=pytz.UTC)
            if program_start_datetime_tzaware < datetime and program_end_datetime_tzaware > datetime:
                return program
        return None


    def start_guide_file_checker_thread(self):
        """
        Starts a thread that calls run method
        """
        gv.logger.info("Guide file checker thread started")
        thread = Thread(target=self.guide_file_checker_run, args=())
        thread.daemon = True
        self.guide_file_thread = thread
        thread.start()

    def guide_file_checker_run(self):
        """Thread run method
        """
        while gv.api_dm is None:
            time.sleep(1)
        while True:
            try:
                self.get_guide_data()
            except FileNotFoundError:
                gv.logger.warn("Guide file not found")
                time.sleep(30)
    
    def get_guide_data(self):
        """[summary]
        """
        if Epg.objects().count() == 0:
            self.process_new_epg()
        else:
            self.check_and_update_current_epg()
        gv.logger.info("Sleeping for 30 seconds...")
        time.sleep(30)

    def check_and_update_current_epg(self):
        with open(self.guide_file,  'r+', encoding="utf-8") as guide_file_open:
            new_guide_data = xmltodict.parse(guide_file_open.read())
            if new_guide_data != self.guide_data and self.is_epg_old():
                self.check_guide_changed(new_guide_data)
            else:
                gv.logger.info("Guide file has not changed")

    def is_epg_old(self):
        current_status = StatusData.objects.order_by('-id').first()
        if self.is_epg_generating:
            return False
        if current_status is None:
            self.is_epg_generating = True
            return True
        if not current_status.is_epg_generating:
            self.is_epg_generating = True
            current_status.update(
                is_epg_generating = True
            )
            current_status.reload()
            return True
        return False

    def check_guide_changed(self, new_guide_data):
        """ Checks after X seconds if the file has changed to know 
            if the file is at generating process """
        seconds_after_guide_data = None
        while (seconds_after_guide_data != new_guide_data):
            gv.logger.warning("Guide is on generating process")
            with open(self.guide_file, encoding="utf-8") as seconds_after_guide_file_open:
                new_guide_data = seconds_after_guide_data
                seconds_after_guide_data = xmltodict.parse(
                    seconds_after_guide_file_open.read())
            seconds_after_guide_file_open.close()
            time.sleep(10) # Sleeps X seconds to let the generating process work
        gv.logger.info("Guide file generated")
        self.guide_data = self.guide_file # if it is different updates the attribute
        self.guide_data_dict = list(self.guide_data.values())[0]
        self.process_new_epg()

    def process_new_epg(self):
        if self.guide_data is not None:   
            gv.logger.info("Saving new EPG to MongoDB")
            self.save_epg_mongo()

    def save_epg_mongo(self):
        try:
            
            epg = self.create_new_epg()
            if (epg.programs.count() != len(self.guide_data_dict["programme"])):
                gv.logger.warn("Different EPG in XML than in DB object, skipping EPG object ...")
                return
            time.sleep(getpid()/100)
            last_epg = Epg.objects.order_by('-id').first()
            if last_epg is not None:
                is_epg_duplicated = self.check_epg_duplicate_in_db(epg, last_epg)
                if is_epg_duplicated:
                    return
            epg.save()
            self.update_epg_generation_status()
        except NotUniqueError as e:
            gv.logger.warn("EPG already saved, skipping ...")
            gv.logger.error(e)
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())

    def create_new_epg(self):
        epg = Epg(**{
            "journey_datetime": self.journey_manager.get_config_journey_datetime(),
            "provider": self.guide_data_dict["channel"][0]["url"],
            "channels": self.get_guide_data_channels(),
            "programs": [],
            "created_at": datetime.now(pytz.utc)
        })

        updated_epg = self.save_programs_to_epg(epg)
        return updated_epg

    
    def save_programs_to_epg(self, epg):
        for program in self.guide_data_dict["programme"]:
            start_datetime = datetime.strptime(program["@start"], self.date_parsing_string)
            end_datetime = datetime.strptime(program["@stop"], self.date_parsing_string)
            program_name = program["title"]["#text"]
            # Adds subtitle if it appears in EPG
            if "sub-title" in program.keys():
                program_name += " " + program["sub-title"]["#text"]
            epg_program = EpgProgram(**{
                "program_name": program_name,
                "channel": program["@channel"],
                "start_datetime": start_datetime,
                "end_datetime": end_datetime
            })
            epg.programs.append(epg_program)
        return epg

    def check_epg_duplicate_in_db(self, epg,  last_epg):
        last_journey_datetime_tz_located = last_epg.journey_datetime.replace(tzinfo=pytz.utc).astimezone(pytz.utc)
        last_created_at_tz_located = last_epg.created_at.replace(tzinfo=pytz.utc).astimezone(pytz.utc)
        are_journeys_duplicate = (last_journey_datetime_tz_located - epg.journey_datetime) < timedelta(seconds=10)
        are_channels_duplicate = last_epg.channels == epg.channels
        are_created_at_same_time = ((epg.created_at - last_created_at_tz_located) < timedelta(seconds=10))
        if are_journeys_duplicate and are_channels_duplicate and are_created_at_same_time:
            return True
        return False
    
    def update_epg_generation_status(self):
        self.is_epg_generating = False
        current_status = StatusData.objects.order_by('-id').first()
        if current_status is not None:
            current_status.update(
                is_epg_generating = False
            )
            current_status.reload()
            current_status.save()

    def get_guide_data_channels(self):
        try:
            channels = []
            if self.guide_data is not None:
                channels = [channel["display-name"]["#text"] for channel in self.guide_data_dict["channel"]]
            return channels
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
