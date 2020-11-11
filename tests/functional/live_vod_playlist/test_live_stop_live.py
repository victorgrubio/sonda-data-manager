import requests
import time
import os
import pytest
from tests import utils

class TestLiveStopLive:

    def test_live_stop_live(self):
        _  = utils.put_config_new_url(url=pytest.STREAM_URL)
        response_launch_live = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_STREAM)
        assert response_launch_live.status_code == 200

        response_stop_live = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_live.status_code == 200

        current_program_live = utils.get_program_parameters(program_name="current")

        response_launch_live2 = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_STREAM)

        assert response_launch_live2.status_code == 200

        response_stop_vod = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_vod.status_code == 200

        previous_program_live = utils.get_program_parameters(program_name="previous")
        current_program_live2 = utils.get_program_parameters(program_name="current")

        assert previous_program_live != {}
        assert previous_program_live == current_program_live
        assert previous_program_live == current_program_live2

        # Clear database content
        utils.clear_database()
