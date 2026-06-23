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


class SaveSnapshotsTests(TestCase):
    fixtures = ["one-forecast.json"]

    def setUp(self):
        print("set up")

    def test_saves_snapshot(self):
        """
        correctly processes the json object of a tracks response
        """

        drifter_forecast: LiveOceanDrifterForecast = LiveOceanDrifterForecast.objects.first()

        drifter_forecast.times = expected_times_response
        drifter_forecast.drifters_forecast = expected_tracks_response

        save_snapshots(
            drifter_forecast
        )

        count = DrifterSnapshot.objects.all().count()
        self.assertEqual(count, 1)
