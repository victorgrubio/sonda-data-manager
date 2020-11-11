import requests
import time
import os
import pytest

from tests import utils

class TestVodLive:

    def test_vod_live(self):

        response_upload_vod = utils.upload_sample_video(filename=pytest.VIDEO_PATH)
        assert response_upload_vod.status_code == 200

        response_put_config = utils.put_config_new_url(url=f"{response_upload_vod.json()['video_path']}")
        assert response_put_config.status_code == 200

        response_launch_vod = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME)
        assert response_launch_vod.status_code == 200

        response_stop_vod = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_vod.status_code == 200

        current_program_vod = utils.get_program_parameters(program_name="current")

        response_put_config = utils.put_config_new_url(url=utils.STREAM_URL)

        response_launch_vod = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME)
        assert response_launch_vod.status_code == 200

        response_stop_vod = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_vod.status_code == 200

        previous_program_vod = utils.get_program_parameters(program_name="previous")
        current_program_live = utils.get_program_parameters(program_name="current")

        assert current_program_vod != {}
        assert current_program_vod == current_program_vod
        assert previous_program_vod != current_program_live

        # Clear database content
        utils.clear_database()




