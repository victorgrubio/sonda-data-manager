import requests
import time
import os
import pytest
from tests import utils

class TestLivePlaylistLive:

    def test_live_playlist_live(self):
        
        response_put_config = utils.put_config_new_url(url=pytest.STREAM_URL)
        response_launch_live = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_STREAM)
        assert response_launch_live.status_code == 200

        response_stop_live = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_live.status_code == 200

        current_program_live1 = utils.get_program_parameters(program_name="current")
        current_journey_live1 = utils.get_journey_parameters(journey_datetime="current")

        response_upload_playlist = utils.upload_sample_video(filename=pytest.PLAYLIST_PATH)
        assert response_upload_playlist.status_code == 200

        response_put_config = utils.put_config_new_url(url=f"{response_upload_playlist.json()['video_path']}")
        assert response_put_config.status_code == 200

        response_launch_playlist = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_PLAYLIST)
        assert response_launch_playlist.status_code == 200

        response_stop_playlist = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_playlist.status_code == 200

        previous_program_live1 = utils.get_program_parameters(program_name="previous")
        current_program_playlist2 = utils.get_program_parameters(program_name="current")
        previous_journey_live1 = utils.get_journey_parameters(journey_datetime="previous")
        current_journey_playlist2 = utils.get_journey_parameters(journey_datetime="current")

        response_put_config = utils.put_config_new_url(url=f"{pytest.STREAM_URL}")

        response_launch_live3 = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_STREAM)
        assert response_launch_live3.status_code == 200

        response_stop_live3 = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_live3.status_code == 200

        previous_program_playlist2 = utils.get_program_parameters(program_name="previous")
        current_program_live3 = utils.get_program_parameters(program_name="current")
        previous_journey_playlist2 = utils.get_journey_parameters(journey_datetime="previous")
        current_journey_live3 = utils.get_journey_parameters(journey_datetime="current")

        assert previous_program_live1 != {}
        assert previous_program_playlist2 != {}
        assert current_program_live3 != {}

        assert previous_program_live1 == current_program_live1
        assert previous_program_live1 != current_program_playlist2
        assert previous_journey_live1 == current_journey_live1
        assert previous_journey_live1 != current_journey_playlist2

        assert previous_program_live1 != current_program_live3
        assert previous_program_playlist2 != current_program_live3
        assert previous_journey_live1 != current_journey_live3
        assert previous_journey_playlist2 != current_journey_live3


        # Clear database content
        utils.clear_database()
