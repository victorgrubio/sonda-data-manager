import requests
import time
import os
import pytest
from tests import utils

class TestPlaylistVodLive:

    def test_playlist_vod_live(self):
       
        response_upload_playlist = utils.upload_sample_video(filename=pytest.PLAYLIST_PATH)
        assert response_upload_playlist.status_code == 200

        response_put_config = utils.put_config_new_url(url=f"{response_upload_playlist.json()['video_path']}")
        assert response_put_config.status_code == 200

        response_launch_playlist = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_PLAYLIST)
        assert response_launch_playlist.status_code == 200

        response_stop_playlist = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_playlist.status_code == 200

        current_program_playlist1 = utils.get_program_parameters(program_name="current")
        current_journey_playlist1 = utils.get_journey_parameters(journey_datetime="current")

        response_upload_vod = utils.upload_sample_video(filename=pytest.VIDEO_PATH)
        assert response_upload_vod.status_code == 200

        response_put_config = utils.put_config_new_url(url=f"{response_upload_vod.json()['video_path']}")
        assert response_put_config.status_code == 200

        response_launch_vod = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME)
        assert response_launch_vod.status_code == 200

        response_stop_vod = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_vod.status_code == 200

        previous_program_playlist1 = utils.get_program_parameters(program_name="previous")
        previous_journey_playlist1 = utils.get_journey_parameters(journey_datetime="previous")
        current_program_vod2 = utils.get_program_parameters(program_name="current")
        current_journey_vod2 = utils.get_journey_parameters(journey_datetime="current")

        response_put_config = utils.put_config_new_url(url=f"{utils.STREAM_URL}")

        response_launch_live3 = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME)
        assert response_launch_live3.status_code == 200

        response_stop_live3 = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_live3.status_code == 200

        previous_program_vod2 = utils.get_program_parameters(program_name="previous")
        previous_journey_vod2 = utils.get_journey_parameters(journey_datetime="previous")
        current_program_live3 = utils.get_program_parameters(program_name="current")
        current_journey_live3 = utils.get_journey_parameters(journey_datetime="current")

        assert previous_program_playlist1 != {}
        assert previous_program_vod2 != {}
        assert current_program_live3 != {}

        assert previous_program_playlist1 == current_program_playlist1
        assert previous_program_playlist1 != current_program_vod2
        assert previous_journey_playlist1 == current_journey_playlist1
        assert previous_journey_playlist1 != current_journey_vod2

        assert previous_program_playlist1 != current_program_live3
        assert previous_program_vod2 != current_program_live3
        assert previous_journey_playlist1 != current_journey_live3
        assert previous_journey_vod2 != current_journey_live3


        # Clear database content
        utils.clear_database()
