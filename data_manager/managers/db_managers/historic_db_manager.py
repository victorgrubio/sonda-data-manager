import traceback
from datetime import datetime
from pyrfc3339 import parse

from helper import global_variables as gv
from db_models import VideoAnalysis
from managers.db_managers import BaseDbManager

class HistoricDbManager(BaseDbManager):
    """Class that represents the handler object use to manage Alerts in MongoDB

    :param db_connection: DbConnection instance to handle MongoDb connection
    :type db_connection: data_manager.managers.DbConnection
    """
    def __init__(self, db_connection):
        """Constructor
        """
        BaseDbManager.__init__(self, db_connection)
        self.raw_search_query = {}
        self.search_data = {}
    
    def search(self, search_type="time", search_data={}):
        """Gets the list of documents resulting from a search using search data provided
        
        :param search_type: Type of search, defaults to "time". Possible values: "journey", "time"
        :type search_type: str, optional
        :param search_data: Data to perform search, defaults to {}. 
        ..note:: 
            Keys: "program_name", "url" are optional and can be used for both time and journey search types. Both parameters are strings.
            For time searchs, "init_datetime" and "end_datetime" should be included. 
            In terms of journey search, only "journey datetime is required".
            Each of these required parameters is a string that represents a datetime in RFC3339 format.
        :type search_data: dict, optional
        :return: The document QuerySet of videoAnalysis documents
        :rtype: mongoengine.QuerySet
        """
        documents_queryset = None
        try: 
            self.search_data = search_data
            if search_type == "time": #search using timestamp
                dict_timestamps = self.get_search_timestamps_parsed()
                self.raw_search_query = {
                    "inserted_at": {
                        "$gte": int(dict_timestamps["init_timestamp"]),
                        "$lte": int(dict_timestamps["end_timestamp"])
                    }
                }
            elif search_type == "journey": # search using journey data
                self.raw_search_query = {'journey_datetime': parse(self.search_data["journey_datetime"])}
            self.update_raw_search_query()
            documents_queryset = self.get_document_queryset_from_search()
        except Exception as e:
            gv.logger.error(e)   
            gv.logger.error(traceback.print_exc())
        return documents_queryset
    
    def get_search_timestamps_parsed(self):
        timestamp_dict = {}
        init_datetime = parse(self.search_data["init_datetime"])
        end_datetime = parse(self.search_data["end_datetime"])
        timestamp_dict["init_timestamp"] = datetime.timestamp(init_datetime)*1000
        timestamp_dict["end_timestamp"] =  datetime.timestamp(end_datetime)*1000
        return timestamp_dict
    
    def get_document_queryset_from_search(self):
        """Returns historic search data as Mongoengine Queryset
        
        :param search_data: Data to perform search, defaults to {}. 
        :type search_data: dict
        :return: Query of documents that match the search requirements
        :rtype: mongoengine.QuerySet
        """
        gv.logger.info(self.raw_search_query)
        documents_queryset = VideoAnalysis.objects(__raw__=self.raw_search_query).order_by("inserted_at")
        return documents_queryset

    def update_raw_search_query(self):
        for field in ["program_name", "url"]:
            if str(self.search_data.get(field)) not in [None, ""]:
                self.raw_search_query.update({
                    f"videoSRC.{field}": str(self.search_data[field])
                })

