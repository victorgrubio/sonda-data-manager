import requests
import time
import os
import pytest

from tests import utils


class TestLivePlaylist:

    def test_live_playlist(self):
        response_put_config = utils.put_config_new_url(url=pytest.STREAM_URL)
        response_launch_live = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_STREAM)
        assert response_launch_live.status_code == 200

        response_stop_live = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_live.status_code == 200

        current_journey_live_1 = utils.get_journey_parameters(journey_datetime="current")

        response_upload_vod = utils.upload_sample_video(filename=pytest.PLAYLIST_PATH)
        assert response_upload_vod.status_code == 200

        response_put_config = utils.put_config_new_url(url=f"{response_upload_vod.json()['video_path']}")
        assert response_put_config.status_code == 200

        response_launch_vod = requests.post(f"{pytest.API_BASE_URL}/probe/launch")
        time.sleep(pytest.LAUNCH_TIME_PLAYLIST)
        assert response_launch_vod.status_code == 200

        response_stop_vod = requests.post(f"{pytest.API_BASE_URL}/probe/stop")
        assert response_stop_vod.status_code == 200

        previous_journey_live_2 = utils.get_journey_parameters(journey_datetime="previous")
        current_journey_playlist_2 = utils.get_journey_parameters(journey_datetime="current")

        assert previous_journey_live_2 != {}
        assert previous_journey_live_2 == current_journey_live_1
        assert previous_journey_live_2 != current_journey_playlist_2

        # Clear database content
        utils.clear_database()

