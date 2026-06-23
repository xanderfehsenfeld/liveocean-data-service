from datetime import datetime

from django.http import JsonResponse, HttpResponse, Http404
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from .models import DrifterSnapshot, Feature, FeatureCollection, FeatureProperties, GeometryPoint, LiveOceanDrifterForecast, Track
import requests
from django.contrib.gis.db import models


# ---------------------------------------------------------------------------
# Core logic  (direct translation of getPoints)
# ---------------------------------------------------------------------------

def get_points(tracks: list[Track]) -> list[FeatureCollection]:
    """
    For every time-step index, build a FeatureCollection that contains one
    Point Feature per drifter track.
    """
    if not tracks or not tracks[0].x:
        return []

    result: list[FeatureCollection] = []

    for time_index in range(len(tracks[0].x)):
        features: list[Feature] = []

        for drifter_id, track in enumerate(tracks):
            latitude = track.y[time_index]
            longitude = track.x[time_index]

            features.append(
                Feature(
                    type="Feature",
                    properties=FeatureProperties(
                        latitude=latitude,
                        longitude=longitude,
                        id=str(drifter_id),
                    ),
                    geometry=GeometryPoint(
                        type="Point",
                        coordinates=(longitude, latitude),
                    ),
                )
            )

        result.append(FeatureCollection(
            type="FeatureCollection", features=features))

    return result


# ---------------------------------------------------------------------------
# Example: bulk-create snapshots from raw track data
# ---------------------------------------------------------------------------


def save_snapshots(tracks: list[Track], times: list[str], forecast_id:  models.ForeignKey[LiveOceanDrifterForecast]) -> list[DrifterSnapshot]:
    """
    Convert raw Track data all the way to persisted DrifterSnapshot rows.

    Usage::

        tracks = [Track(x=[...], y=[...]), ...]
        snapshots = save_snapshots(tracks)
    """
    feature_collections = get_points(tracks)
    snapshots = [
        DrifterSnapshot.from_feature_collection(i, fc, times[i])
        for i, fc in enumerate(feature_collections)
    ]
    return DrifterSnapshot.objects.bulk_create(snapshots)


def forecast_drifters(request, tracks_filename, times_filename):

    current_date = datetime.now().date()

    result = LiveOceanDrifterForecast.objects.filter(
        date_of_query=current_date,

        tracks_filename=tracks_filename).first()

    if (result is None):
        # make http get request to get drifter data

        base_url = "https://s3.kopah.uw.edu/liveocean-web/{}"
        drifters_forecast = requests.get(
            base_url.format(tracks_filename),).json()
        times = requests.get(base_url.format(times_filename)).json()
        result = LiveOceanDrifterForecast(
            drifters_forecast=drifters_forecast,
            date_of_query=current_date,
            times=times,

            name="{}, {} for {}".format(
                tracks_filename, times_filename, current_date),
            tracks_filename=tracks_filename,
        )

        result.save()

    return JsonResponse(result.toJSON(), safe=False)
