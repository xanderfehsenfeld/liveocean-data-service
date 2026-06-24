from dataclasses import dataclass
from datetime import datetime

from django.contrib.gis.db import models
from django.forms.models import model_to_dict
from django.contrib.gis.geos import MultiPoint, Point

from dataclasses import dataclass, field
from typing import Literal

from zoneinfo import ZoneInfo

import json


class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField("Population 2005")
    fips = models.CharField("FIPS Code", max_length=2, null=True)
    iso2 = models.CharField("2 Digit ISO", max_length=2)
    iso3 = models.CharField("3 Digit ISO", max_length=3)
    un = models.IntegerField("United Nations Code")
    region = models.IntegerField("Region Code")
    subregion = models.IntegerField("Sub-Region Code")
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name


class LiveOceanDrifterForecast(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    date_of_query = models.DateField("Date of query")
    drifters_forecast = models.JSONField("JSON Response")
    tracks_filename = models.CharField("Tracks file name", max_length=50)

    times = models.JSONField("Times")

    def toJSON(self):
        return model_to_dict(self)


class Drifter(models.Model):
    location = models.PointField("location")
    forecast = models.ForeignKey(
        LiveOceanDrifterForecast, on_delete=models.CASCADE)
    timestamp = models.TimeField("Time")
    drifter_id = models.IntegerField("ID within forecast")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Track:
    x: list[str]
    y: list[str]


@dataclass
class GeometryPoint:
    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float] = (0.0, 0.0)


@dataclass
class FeatureProperties:
    latitude: float
    longitude: float
    id: str


@dataclass
class Feature:
    type: Literal["Feature"] = "Feature"
    properties: FeatureProperties = field(
        default_factory=lambda: FeatureProperties(0, 0, ""))
    geometry: GeometryPoint = field(default_factory=GeometryPoint)


@dataclass
class FeatureCollection:
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[Feature] = field(default_factory=list)

# ---------------------------------------------------------------------------
# GeoDjango model
# ---------------------------------------------------------------------------


ABBREV_TO_IANA = {

    "PDT": "America/Los_Angeles",
    "PST": "America/Los_Angeles",
    "MDT": "America/Denver",
    "MST": "America/Denver",
    "CDT": "America/Chicago",
    "CST": "America/Chicago",
    "EDT": "America/New_York",
    "EST": "America/New_York",
}


def date_string_to_datetime(date_string: str) -> datetime:
    # example date_string = "06/22/2026 - 05PM PDT"

    datetime_part, timezone_abbreviation = date_string.rsplit(" ", 1)

    naive_datetime: datetime = datetime.strptime(
        datetime_part.strip(), "%m/%d/%Y - %I%p")
    iana_tz = ABBREV_TO_IANA[timezone_abbreviation]
    return naive_datetime.replace(tzinfo=ZoneInfo(iana_tz))


class DrifterSnapshot(models.Model):
    """
    Stores one time-step snapshot as a GeoDjango MultiPoint.

    Each point in ``locations`` corresponds to a single drifter's position at
    ``time_index``.  The ``drifter_ids`` JSON field preserves the original
    string IDs so rows can be reconstructed into FeatureCollections later.
    """

    pk = models.CompositePrimaryKey("forecast_id", "time_index")
    forecast_id = models.ForeignKey(
        LiveOceanDrifterForecast, on_delete=models.CASCADE)

    time_index = models.PositiveIntegerField(
        help_text="Zero-based index into the original time series.",
    )

    locations = models.MultiPointField(
        srid=4326,
        help_text="WGS-84 MultiPoint: one point per drifter at this time-step.",
        geography=True
    )
    drifter_ids = models.JSONField(
        default=list,
        help_text="Ordered list of drifter ID strings matching each point.",
    )

    time = models.DateTimeField(
        "The timestamp within the forecast corresponding to this snapshot")

    class Meta:
        ordering = ["time_index"]
        verbose_name = "Drifter Snapshot"
        verbose_name_plural = "Drifter Snapshots"

    def __str__(self) -> str:
        return f"DrifterSnapshot(time_index={self.time_index}, n_drifters={len(self.drifter_ids)})"

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_feature_collection(
        cls, time_index: int, fc: FeatureCollection, time: str,

        forecast: models.ForeignKey[LiveOceanDrifterForecast]
    ) -> "DrifterSnapshot":
        """Build (but do not save) a DrifterSnapshot from a FeatureCollection."""
        geos_points = [
            Point(float(f.geometry.coordinates[0]),
                  float(f.geometry.coordinates[1]), srid=4326)
            for f in fc.features
        ]

        return cls(
            forecast_id=forecast,
            time_index=time_index,
            locations=MultiPoint(*geos_points, srid=4326),
            drifter_ids=[f.properties.id for f in fc.features],
            time=date_string_to_datetime(time)
        )

    def to_feature_collection(self) -> FeatureCollection:
        """Reconstruct a FeatureCollection from this model instance."""
        features = [
            Feature(
                properties=FeatureProperties(
                    latitude=pt.y,
                    longitude=pt.x,
                    id=self.drifter_ids[i],
                ),
                geometry=GeometryPoint(coordinates=(pt.x, pt.y)),
            )
            for i, pt in enumerate(self.locations)
        ]
        return FeatureCollection(features=features)

    def toJSON(self):

        locations: MultiPoint = self.locations
        model_as_dict = model_to_dict(self, exclude=["locations"])
        model_as_dict["locations"] = json.loads(locations.geojson)
        return model_as_dict
