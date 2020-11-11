import requests
import utils
import os
from pymongo import MongoClient

API_BASE_URL = "http://0.0.0.0:{}/videoAnalysis".format(os.getenv("API_PORT"))
DB_HOST = "127.0.0.1"
DB_PORT = int(os.getenv("DB_PORT"))
API_PORT = os.getenv("API_PORT")
DB_NAME = "VideoDB"

def get_program_parameters( program_name="current"):
        program = {}
        parameters = ["data", "mos", "mos-percentages", "alert-list", "alert-number"]
        for param in parameters:
            response_data = requests.get(f"{API_BASE_URL}/programs/{program_name}/{param}").content
            program[param] = response_data
        return program


def get_journey_parameters(journey_datetime="current"):
    journey = {}
    parameters = ["mos", "mos-percentages", "alert-list", "alert-number"]
    for param in parameters:
        response_data = requests.get(f"{API_BASE_URL}/journeys/{journey_datetime}/{param}").content
        journey[param] = response_data
    return journey


def upload_sample_video(filename=""):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    response_upload_vod = requests.post(f"{API_BASE_URL}/vod/upload",
        files={"file": 
            (f"{filename}",
            open(f"{current_dir}/data/{filename}", "rb"),
            "multipart/form-data",
            {'Expires': '0'},
            )
        }
    )
    return response_upload_vod


def put_config_new_url(url="url"):
    response_put_config = requests.put(f"{API_BASE_URL}/probe/config",
        headers={"Content-type": "application/json"},
        json={
                "alert_mos_threshold": 3.0,
                "channel_name": "TEST CHANNEL",
                "journey_duration": 1440,
                "journey_start_time": 0,
                "mode": "complete",
                "mos_excellent": 4.1,
                "mos_good": 4.0,
                "mos_regular": 2.0,
                "program_duration": 120,
                "samples": -1,
                "url": url,
                "warning_mos_threshold": 4.0
            }
        )
    return response_put_config


def clear_database():
    # Clear database content
    mongo_client = MongoClient(DB_HOST, DB_PORT)
    mongo_client.drop_database(DB_NAME)