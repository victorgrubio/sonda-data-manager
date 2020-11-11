import requests
import time
import os
import pytest
from tests import utils

class TestLiveVod:

    def test_live_vod(self):

        response_put_config = utils.put_config_new_url(url=pytest.STREAM_URL)
        response_launch_live = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_STREAM)
        assert response_launch_live.status_code == 200

        response_stop_live = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_live.status_code == 200

        current_program_live = utils.get_program_parameters(program_name="current")

        response_upload_vod = utils.upload_sample_video(filename=pytest.VIDEO_PATH)
        assert response_upload_vod.status_code == 200

        response_put_config = utils.put_config_new_url(url=f"{response_upload_vod.json()['video_path']}")

        assert response_put_config.status_code == 200

        response_launch_vod = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_VOD)

        assert response_launch_vod.status_code == 200

        response_stop_vod = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_vod.status_code == 200

        previous_program_live = utils.get_program_parameters(program_name="previous")
        current_program_vod = utils.get_program_parameters(program_name="current")

        assert previous_program_live != {}
        assert previous_program_live == current_program_live
        assert previous_program_live != current_program_vod

        # Clear database content
        utils.clear_database()
