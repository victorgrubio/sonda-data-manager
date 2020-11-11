import requests
import time 
from pymongo import MongoClient

from tests import utils
import pytest

class TestVideoQualityProbe:

    def test_status(self):
        url = "{}/probe/status".format(pytest.API_BASE_URL)
        # Send a request to the mock API server and store the response.
        response = requests.get(url)

        # Confirm that the request-response cycle completed successfully.
        assert response.status_code == 200

    def test_launch(self):
        url = "{}/probe/launch".format(pytest.API_BASE_URL)
        # Send a request to the mock API server and store the response.
        response = requests.post(url)
        time.sleep(5)
        # Confirm that the request-response cycle completed successfully.
        assert response.status_code == 200

    def test_stop(self):
        url = "{}/probe/stop".format(pytest.API_BASE_URL)
        # Send a request to the mock API server and store the response.
        response = requests.post(url)

        # Confirm that the request-response cycle completed successfully.
        assert response.status_code == 200
        
        # Clear database content
        utils.clear_database()