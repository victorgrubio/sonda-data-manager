import json
from pathlib import Path
from csv import DictWriter
from bson import json_util
from mongoengine import DoesNotExist, fields
from datetime import datetime
from pyrfc3339 import parse
from dateutil.tz import tzlocal
from collections import OrderedDict
import pytz
import os
import time

from helper import global_variables as gv
from helper import config as cfg
from db_models import VideoAnalysis, StatusData


class FileManager:
    """This class represent the object that handles files for VideoMOS system
    """

    def __init__(self, documents=[], alert_events={}, search_data={}, filetype=""):
        self.documents = documents
        self.alert_events = alert_events
        self.search_data = search_data
        self.filetype = filetype    

    def generate_search_file(self):
        """Writes a file in JSON or CSV format containing a list of measures
        """
        server_filename = ""
        base_filename = ""
        folder_file = self.get_folder_file()
        base_path = f"{cfg.data_manager_path}/static/{folder_file}"
        base_filename = self.create_filename_from_search_data()
        server_filename = f'{base_path}/{base_filename}'
        if self.is_file_new(server_filename):
            gv.logger.info("Generating new file")
            self.generate_new_file(server_filename)
        return base_filename

    def get_folder_file(self):
        """ """
        folder_file = ""
        for folder, extension_list in cfg.dict_filetypes.items():
            for extension in extension_list:
                if self.filetype in extension:
                    folder_file = folder
                    break
        return folder_file
    
    def create_filename_from_search_data(self):
        """[summary]
        """
        filename = ""
        if self.search_data.get("init_datetime") is not None:
            filename = self.create_time_search_filename()
        elif self.search_data.get("journey_datetime") is not None:
            filename = self.create_journey_search_filename()
        return filename
        
    def create_time_search_filename(self):
        """[summary]
        """
        init_datetime = parse(self.search_data.get("init_datetime"))
        end_datetime = parse(self.search_data.get("end_datetime"))
        filename = "-".join([
                    init_datetime.strftime("%Y_%m_%d-%H_%M_%S"),
                    end_datetime.strftime("%Y_%m_%d-%H_%M_%S")
                ])
        filename += f'.{self.filetype}'
        return filename

    def create_journey_search_filename(self):
        """[summary]
        """
        filename = ""
        journey_datetime = parse(self.search_data.get("journey_datetime"))
        # Get journey datetime in backend timezone
        localized_journey_datetime = datetime.fromtimestamp(datetime.timestamp(journey_datetime))
        string_localized_journey_datetime = localized_journey_datetime.strftime("%Y_%m_%d-%Hh_%Mm")
        # Add channel name info (without spaces)
        channel_name = self.documents[0]["videoSRC"]["service_name"].replace(" ", "_")
        filename = "-".join([channel_name, string_localized_journey_datetime])
        # If we have program information, add the name, init time and endtime of it
        filename = self.update_filename_with_program(filename)
        filename += f".{self.filetype}"
        return filename

    def update_filename_with_program(self, filename):
        """ """
        dict_filename_fields = {}
        if self.search_data.get("program_name") not in [None, ""]:
            dict_filename_fields["program_name"] = self.search_data.get("program_name").replace(" ","_").replace("/","_")
            datetime_dicts = self.generate_filename_datetimes_dict()
            dict_filename_fields.update(datetime_dicts)
            filename = "-".join([filename,
                "Program_"+dict_filename_fields["program_name"],
                dict_filename_fields["init_datetime"],
                dict_filename_fields["end_datetime"]
            ])
        return filename
    
    def generate_filename_datetimes_dict(self):
        """[summary]
        """
        datetime_dict = {}
        init_timestamp = int(self.documents.first().inserted_at/1000)
        end_timestamp = int(self.documents.order_by('-id').first().inserted_at/1000)
        datetime_dict["init_datetime"] = datetime.fromtimestamp(init_timestamp).strftime("%Hh_%Mm")
        datetime_dict["end_datetime"] = datetime.fromtimestamp(end_timestamp).strftime("%Hh_%Mm")
        return datetime_dict

    def is_file_new(self, server_filename):
        """[summary]
        """
        if self.search_data.get("init_datetime") is not None:
            return True
        return self.is_journey_search_file_new(server_filename)

    def is_journey_search_file_new(self,  server_filename):
        current_status = StatusData.objects.order_by('-id').first()
        if current_status is None:
            return True
        is_program_name_empty = self.search_data.get("program_name") in [None, ""]
        is_file_new = not os.path.exists(server_filename)
        current_journey = current_status.journey_datetime.replace(tzinfo=pytz.UTC)
        is_current_journey = current_journey == parse(self.search_data.get("journey_datetime"))
        return is_program_name_empty or is_file_new or is_current_journey

    def generate_new_file(self, server_filename):
        """ """
        gv.logger.info("Generating new search file ...")
        if self.filetype == "csv":
            self.generate_csv_file(server_filename)
        elif self.filetype == "json":
            with open(server_filename, "w") as output_file:
                output_file.write(self.documents.to_json())

    def generate_csv_file(self, server_filename):
        """Creates the CSV file correspondent to the list of documents provided
        """
        with open(server_filename,'w',encoding='utf-8-sig') as output_file:
            csv_writer = None
            for index, document in enumerate(self.documents):
                csv_row_dict = self.get_new_csv_row(document)
                if index == 0:
                    csv_writer = DictWriter(output_file, fieldnames=list(csv_row_dict.keys()))
                    csv_writer.writeheader()
                csv_writer.writerow(csv_row_dict)

    def get_new_csv_row(self, document):
        """Completes the CSV row info from alerts and document stats"""
        alerts_document = self.check_document_alert_events(document)
        csv_row_dict = self.get_csv_row_from_document_fields(document)
        csv_row_dict.update({
            "alerts": alerts_document
        })
        return csv_row_dict

    def check_document_alert_events(self, document):
        """[summary]        """
        document_alert_events = []
        for event_category in self.alert_events.keys():
            document_alert_events += self.check_category_events_in_document(document, event_category)
        return document_alert_events

    def check_category_events_in_document(self, document, event_category):
        """[summary]        """
        document_alert_events = []
        try:
            # event_category comes in plural, we have to made it singular to append it to csv
            event_category_singular = event_category[:-1]
            for alert_event in self.alert_events[event_category]:
                # Check if document that has alert is our current document
                if alert_event["video_analysis"]["$oid"] == str(document.id):
                    document_alert_events.append(f"{event_category_singular}_{alert_event['category']}")
            return document_alert_events
        except Exception:
            return document_alert_events
    
    def get_csv_row_from_document_fields(self, document):
        """ """
        csv_row_dict = OrderedDict()
        document_fields = set(VideoAnalysis._fields.keys())
        embedded_document_fields = set([k for k,v in VideoAnalysis._fields.items() if type(v) is fields.EmbeddedDocumentField])  
        simple_document_fields = document_fields.difference(embedded_document_fields)
        for field in simple_document_fields:
            csv_row_dict = self.update_csv_row_with_field(document, field, csv_row_dict)
        for field in embedded_document_fields:
            csv_row_dict = self.update_csv_row_with_embedded_document_field(document, field, csv_row_dict)
        return csv_row_dict

    def update_csv_row_with_field(self, document, field, csv_row_dict):
        """ """
        row_data = ""
        if field == "id":
            row_data = str(document.id)
        elif field == "journey_datetime":
            row_data = document[field].replace(tzinfo=pytz.UTC).astimezone(tzlocal())
        else:
            row_data = document[field]
        csv_row_dict.update({field: row_data})
        return csv_row_dict

    def update_csv_row_with_embedded_document_field(self, document, field, csv_row_dict):
        """ """
        document_as_dict = json.loads(document.to_json())
        sub_field_prefix = self.get_subfield_prefix(field)
        for sub_field_name, sub_field_value in document_as_dict[field].items():
            csv_row_dict.update({
                f"{sub_field_prefix}{sub_field_name}": sub_field_value})
        return csv_row_dict

    def get_subfield_prefix(self, field):
        if field == "audioSettings":
            return "audio_"
        return ""

class file_utils:
    @staticmethod
    def remove_old_files():
        now = time.time()
        for extension in ["csv", "json"]:
            base_path = f"{cfg.data_manager_path}/static/{extension}"
            for filename in os.listdir(base_path):
                file_path = os.path.join(base_path, filename)
                if os.stat(file_path).st_mtime < now - 7 * 86400: # Older than a week
                    if os.path.isfile(file_path) and extension in filename:
                        os.remove()