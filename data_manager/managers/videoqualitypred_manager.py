'''
Created on 18 mar. 2020

@author: victor
'''
import json
import ast
import requests
import time

from helper import config as cfg
from helper import global_variables as gv


class VideoQualityPredManager:
    """
    This class is the handler that manages the requests/responses of the Video Quality Analysis module.
    """
    def __init__(self):
        pass
    
    def post_api_mos_analyzer(self, body, headers):
        """
        Sends data to Video Quality Analysis module and obtains a prediction
        
        :return: Prediction data response from VideoQA
        :rtype: requests.Response
        """
        response = None
        try:
            # 1) Prepare URL
            api_endpoint = f"http://{cfg.ai_host}:{cfg.ai_port}/VideoQA/predict/{cfg.predict_strategy}"
            # 2) POST Data
            if isinstance(body, str):
                data = ast.literal_eval(body)
            else:
                data = body

            response = requests.post(url=api_endpoint, data=json.dumps(data), headers=headers)

        except Exception as e:
            gv.logger.error(e)
        return response

    def prepare_data_to_db(self, data_content_input, data_content_output, headers=None):
        """
        Preprocesses documents from Video Quality Probe to be inserted into the database
        
        :param data_content_input: Input data, obtained from Probe
        :type data_content_input: str
        :param data_content_output: Output data to be inserted into the DB
        :type data_content_output: str
        :param headers: Information of the request, specifying the mode of the analysis,
         defaults to None
        :type headers: dict, optional
        :return: The postprocessed document
        :rtype: dict
        """
        response = {}
        try:
            # String to dict
            if isinstance(data_content_input, str):
                data_content_input = ast.literal_eval(data_content_input)
            if isinstance(data_content_output, str):
                data_content_output = ast.literal_eval(data_content_output)

            # Merged Data
            response.update(data_content_input)
            if headers is not None:
                if "Mode" in headers.keys():
                    response.update({"mode": headers["Mode"]})
            response.update({"inserted_at": int(time.time()*1000)})
            response.update({"mosAnalysis": data_content_output})

        except Exception as e:
            gv.logger.error(e)
        return response

    def send_anomaly_data(self, data):
        response = None
        try:
            api_endpoint = f"http://{cfg.ai_host}:{cfg.ai_port}/VideoQA/anomalies/knn"
            response = requests.post(url=api_endpoint, data=json.dumps(data))
            gv.logger.info(response.json())
        except Exception as e:
            gv.logger.error(e)
        return response