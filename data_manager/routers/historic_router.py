'''
Created on 17 mar. 2020

@author: victor
'''
import traceback
from itertools import starmap
from pyrfc3339 import parse
from helper import global_variables as gv
from helper import config as cfg
from helper import utils
from managers import FileManager

class HistoricRouter:
    """A class that represents the router in charge of handling DataManager API Historic Blueprint methods
        
    :param historic_db_manager: DbManager in charge of handling ProbeConfig historic data in MongoDB
    :type historic_db_manager: managers.db_managers.ConfigDbManager
    :param journey_db_manager: DbManager in charge of handling ProbeConfig journeys in MongoDB
    :type journey_db_manager: managers.db_managers.ConfigDbManager
    :param alert_db_manager: DbManager in charge of handling ProbeConfig alerts in MongoDB
    :type alert_db_manager: managers.db_managers.ConfigDbManager
    :param mos_calculator: Manager in charge of handling operations with MOS in MongoDB
    :type mos_calculator: managers.db_managers.MosCalculator
    """
    
    def __init__(self, historic_db_manager, journey_db_manager, alert_db_manager, mos_calculator):
        """Constructor
        """
        self.historic_db_manager = historic_db_manager
        self.journey_db_manager = journey_db_manager
        self.alert_db_manager = alert_db_manager
        self.mos_calculator = mos_calculator
        self.file_manager = FileManager()
        self.search_data = {}

    def get_historic_search(self, search_data):
        """Gets the historic data from a specific search using provided data

        API Endpoint: '/videoAnalysis/search/data', methods=['POST']
        
        :param search_data: Data to perform search, defaults to {}. 
        Keys: "program_name", "url" are optional and can be used for both time and journey search types. Both parameters are strings.
        For time searchs, "init_datetime" and "end_datetime" should be included. 
        In terms of journey search, only "journey datetime is required".
        Each of these required parameters is a string that represents a datetime in RFC3339 format.
        :type search_data: dict, optional
        :return: Dict containing all the information for the historic data representation
        :rtype: dict
        """
        try:
            alert_list = []
            response = {}
            self.search_data = search_data
            if search_data.get("init_datetime") is not None:
                init_datetime = parse(search_data.get("init_datetime"))
                end_datetime = parse(search_data.get("end_datetime"))
                videoanalysis_queryset = self.historic_db_manager.search(
                    search_type="time", search_data=search_data)
                alert_list = self.alert_db_manager.get_alert_warning_list_by_datetime(
                    init_datetime=init_datetime, end_datetime=end_datetime)
            elif search_data.get("journey_datetime") is not None:
                videoanalysis_queryset = self.historic_db_manager.search(
                    search_type="journey", search_data=search_data)
                # If includes program for searching or doesn't
                if search_data.get("program_name") is not None:
                    alert_list = self.alert_db_manager.get_alert_warning_list(
                        journey_datetime=parse(search_data.get("journey_datetime")),
                        program_name=str(search_data.get("program_name"))
                    )
                else:
                    alert_list = self.alert_db_manager.get_alert_warning_list(
                        journey_datetime=parse(search_data.get("journey_datetime"))
                    )
            response = self.get_historic_videoanalysis_data(videoanalysis_queryset, alert_list)
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return response
    

    def get_historic_search_url(self, search_data):
        """Generates a file from a historic search by using the specified data. Returns the url to access this file.

        API Endpoint: '/videoAnalysis/search/url', methods=['POST']
        
        :param search_data: Data to perform search, defaults to {}. 
        Keys: "program_name", "url" are optional and can be used for both time and journey search types. Both parameters are strings.
        For time searchs, "init_datetime" and "end_datetime" should be included. 
        In terms of journey search, only "journey datetime is required".
        Each of these required parameters is a string that represents a datetime in RFC3339 format.
        :type search_data: dict, optional
        :raises Exception: Any possible unhandled exception
        :return: Url to get the file resultant from search
        :rtype: str
        """
        documents = None
        file_url = ""
        alert_list = []
        try:
            self.search_data = search_data
            # Datetime interval search
            if search_data.get("init_datetime") is not None:
                init_datetime = parse(search_data.get("init_datetime"))
                end_datetime = parse(search_data.get("end_datetime"))
                documents = self.historic_db_manager.search(
                    search_type="time", search_data=search_data)
                alert_list = self.alert_db_manager.get_alert_warning_list_by_datetime(
                    init_datetime=init_datetime, end_datetime=end_datetime)
            # Journey search
            elif search_data.get("journey_datetime") is not None:
                documents = self.historic_db_manager.search(
                    search_type="journey", search_data=search_data)
                alert_list = self.alert_db_manager.get_alert_warning_list(
                    journey_datetime=parse(search_data.get("journey_datetime")) )
            filetype = search_data.get("type").lower()
            self.file_manager = FileManager(documents, alert_list, search_data, filetype)
            for cfg_type in cfg.historic_filetypes_allowed:
                if filetype == cfg_type:
                    file_url = self.file_manager.generate_search_file()
                    break
            if file_url == "":
                raise AttributeError(f"File extension {filetype} is not valid for this method. Try json or csv")
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        server_file_url = f"files/{file_url}"
        return server_file_url


    def get_historic_videoanalysis_data(self, videoanalysis_queryset, alert_list):
        """Gets the historic data format from the videoanalysis_queryset obtained by a search process
        
        :param videoanalysis_queryset: List of videoanalysis_queryset from search process
        :type videoanalysis_queryset: list[dict]
        :param alert_list: List of alerts from search process
        :type alert_list: list[dict]
        :return: Historic data from search process
        :rtype: dict
        """
        try:
            if videoanalysis_queryset.count() == 0:
                raise AttributeError("No documents in search")
            width = videoanalysis_queryset.distinct("videoSettings.width")[0]
            height = videoanalysis_queryset.distinct("videoSettings.height")[0]
            frame_rate = videoanalysis_queryset.distinct("videoSettings.frame_rate")[0]
            historic_data = {}
            historic_data["color_space"] = "RGB"
            historic_data["pixel_format"] = videoanalysis_queryset.distinct("videoSettings.pix_format")[0]
            historic_data["scan_type"] = videoanalysis_queryset.distinct("videoSettings.scan_type")[0]
            historic_data["video_codec"] = videoanalysis_queryset.distinct("videoSettings.codec")[0]
            historic_data["resolution"] = f"{width} x {height} {frame_rate}"
            historic_data["url"] = videoanalysis_queryset.distinct("videoSRC.url")[0]
            historic_data["analysis_mode"] = videoanalysis_queryset.distinct("mode")[0]
            historic_data["mos"] = videoanalysis_queryset.average("mosAnalysis.mos")
            historic_data["mos_percentages"] = self.mos_calculator.calculate_mos_categories_videoanalysis_queryset(videoanalysis_queryset)
            historic_data["spat_inf_avg"] = videoanalysis_queryset.average('videoSettings.spat_inf_avg')
            historic_data["temp_inf_avg"] = videoanalysis_queryset.average('videoSettings.temp_inf_avg')
            historic_data["bitrate"] = videoanalysis_queryset.average("videoSettings.bitrate")
            historic_data["warnings"] = alert_list["warnings"]
            historic_data["warning_number"] = len(alert_list["warnings"])
            historic_data["alerts"] = alert_list["alerts"]
            historic_data["alert_number"] = len(alert_list["alerts"])
            historic_data["graph_data"] = self.get_historic_graph_data(videoanalysis_queryset)
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
        return historic_data
    
    def get_historic_graph_data(self, videoanalysis_queryset):
        """Obtains the graph data required to draw the histogram
        
        :param videoanalysis_queryset: videoanalysis_queryset to generate the graph data. db_models.VideoAnalysisDocument as dict
        :type videoanalysis_queryset: dict
        :raises Exception: Any possible unhandled exception
        :return: Historic graph data from videoanalysis_queryset. List of dict with mos, pts and timestamp as keys
        :rtype: List of dicts
        """
        historic_graph_data = []
        if videoanalysis_queryset.count() == 0:
            raise AttributeError("No data in that period of time")
        # GRAPH DATA AS IN PROGRAM
        time_field = self.get_time_field(videoanalysis_queryset) 
        graph_data_tuple_list = videoanalysis_queryset.scalar(time_field, "mosAnalysis__mos", "videoSettings__pts")
        historic_graph_data = list(starmap(self.historic_graph_formatting, graph_data_tuple_list))
        return historic_graph_data

    def get_time_field(self, videoanalysis_queryset):
        url = videoanalysis_queryset.distinct("videoSRC.url")[0]
        content_type = self.get_content_type_by_url(url)
        time_field = "timestamp"
        # Only for vod/playlist programs we use videoSecond, elsewhere timestamp
        if  content_type != "live" and "program_name" in self.search_data:
            time_field = "videoSettings__video_second"
        return time_field

    def get_content_type_by_url(self, url):
        if "/tmp" in url:
            return "vod"
        return "live" 

    def historic_graph_formatting(self, timestamp, mos, pts):
        return {"timestamp": timestamp, "mos": mos, "pts": pts}