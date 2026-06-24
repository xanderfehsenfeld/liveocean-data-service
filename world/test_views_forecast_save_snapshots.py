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
        self.drifter_forecast: LiveOceanDrifterForecast = LiveOceanDrifterForecast.objects.first()

        self.drifter_forecast.times = expected_times_response
        self.drifter_forecast.drifters_forecast = expected_tracks_response

    def test_saves_snapshot(self):
        """
        correctly processes the json object of a tracks response
        """

        save_snapshots(
            self.drifter_forecast
        )

        count = DrifterSnapshot.objects.all().count()
        self.assertEqual(count, 1)

    def test_is_idempotent(self):
        """
        Is idempotent - calls method twice with same parameters
        """

        save_snapshots(
            self.drifter_forecast
        )

        save_snapshots(
            self.drifter_forecast
        )

        count = DrifterSnapshot.objects.all().count()
        self.assertEqual(count, 1)
