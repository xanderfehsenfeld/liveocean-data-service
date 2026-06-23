import datetime
import responses
from responses import matchers

from django.test import SimpleTestCase, Client, TestCase

from datetime import datetime
from unittest import mock

from world.views import save_snapshots

from .models import DrifterSnapshot, LiveOceanDrifterForecast, Track

import mock


expected_times_response = [
    {
        "t": [
            "06/22/2026 - 05PM PDT"

        ]
    }
]


expected_tracks_response = [

    {
        "x": [
            "-122.786"

        ],
        "y": [
            "49.000"

        ]
    }
]


class LiveOceanDrifterForecastViewTests(TestCase):

    fixtures = ["one-forecast.json"]
    times_file = "PS_times.json"
    tracks_file = "PS_tracks.json"

    def setUp(self):

        # Configure test client.
        self.client = Client()

        # Configure mocked responses from upstream endpoint
        upstream_endpoint = "https://s3.kopah.uw.edu/liveocean-web/{}"

        self.times_response = responses.add(
            responses.GET,
            upstream_endpoint.format(self.times_file),
            json=expected_times_response,
            status=200,
            content_type='application/json'
        )

        self.tracks_response = responses.add(
            responses.GET,
            upstream_endpoint.format(self.tracks_file),
            json=expected_tracks_response,
            status=200,
            content_type='application/json'
        )

        responses.add(
            responses.GET,
            '*',
            status=404,
        )

        # Select the forecast from the test
        self.test_forecast = LiveOceanDrifterForecast.objects.first()

    @responses.activate
    @mock.patch('world.views.datetime')
    def test_processes_json_into_correct_form(self, mocked_datetime):
        """
        correctly hits cache when a drifter forecast is present in the database
        """

        mocked_datetime.now.return_value = datetime.combine(
            self.test_forecast.date_of_query, datetime.now().time())
        self.assertIsNotNone(self.test_forecast)

        api_endpoint = "/api/forecast/drifters/{}-{}".format(
            self.tracks_file,  self.times_file,)

        result = self.client.get(api_endpoint)

        self.assertIs(self.times_response.call_count, 0,
                      "Upstream times source was called")
        self.assertIs(self.tracks_response.call_count, 0,
                      "Upstream tracks source was called")

        json = result.json()

        self.assertEqual(json["name"], self.test_forecast.name)

        returned_date = datetime.strptime(
            json["date_of_query"], '%Y-%m-%d').date()
        self.assertEqual(returned_date,
                         self.test_forecast.date_of_query)

    @responses.activate
    @mock.patch('world.views.datetime')
    def test_requests_upstream_when_cache_miss(self, mocked_datetime):
        """
        Correctly misses cache when not present in the database. Creates a new forecast.
        """

        # Mock the correct date to not be in the database
        mocked_date = datetime(1993, 1, 1)
        mocked_datetime.now.return_value = mocked_date

        api_endpoint = "/api/forecast/drifters/{}-{}".format(
            self.tracks_file,  self.times_file,)

        result = self.client.get(api_endpoint)

        self.assertIs(self.times_response.call_count, 1,
                      "Upstream times source was not called")
        self.assertIs(self.tracks_response.call_count, 1,
                      "Upstream tracks source was not called")

        json = result.json()

        self.assertNotEqual(json["name"], self.test_forecast.name)

        created_forecast = LiveOceanDrifterForecast.objects.filter(
            date_of_query=mocked_date
        ).first()

        self.assertIsNotNone(
            created_forecast, "Forecast should have been created.")

    @responses.activate
    @mock.patch('world.views.datetime')
    def test_returns_upstream_errors(self, mocked_datetime):
        """
        correctly returns not found error for upstream not found
        """

        # Mock the correct date to not be in the database
        mocked_date = datetime(1993, 1, 1)
        mocked_datetime.now.return_value = mocked_date

        api_endpoint = "/api/forecast/incorrect-endpoint"

        result = self.client.get(api_endpoint)

        self.assertEqual(result.status_code, 404)

        created_forecast = LiveOceanDrifterForecast.objects.filter(
            date_of_query=mocked_date
        ).first()

        self.assertIsNone(created_forecast,
                          "Forecast should not have been created.")


class SaveSnapshotsTests(TestCase):

    def test_saves_snapshot(self):
        """
        correctly processes the json object of a tracks response
        """

        list_of_tracks: list[Track] = []

        for track in expected_tracks_response:
            list_of_tracks.append(Track(x=track["x"], y=track["y"]))

        self.assertIsNotNone(LiveOceanDrifterForecast.objects.all())
        save_snapshots(
            list_of_tracks, expected_times_response[0]["t"], LiveOceanDrifterForecast.objects.first())

        count = DrifterSnapshot.objects.all().count()
        self.assertEqual(count, 0)
