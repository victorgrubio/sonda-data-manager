import pytest
import utils

def pytest_configure():
    pytest.API_BASE_URL = utils.API_BASE_URL
    pytest.DB_HOST = utils.DB_HOST
    pytest.DB_PORT = utils.DB_PORT
    pytest.API_PORT = utils.API_PORT
    pytest.DB_NAME = utils.DB_NAME
    pytest.LAUNCH_TIME_STREAM = 20
    pytest.LAUNCH_TIME_VOD = 10
    pytest.LAUNCH_TIME_PLAYLIST = 10
    pytest.VIDEO_PATH = "BigBuckBunny_30s_720.mp4"
    pytest.PLAYLIST_PATH = "playlist.mvs"
    pytest.STREAM_URL = "udp://224.0.1.3:5678"
    
    
