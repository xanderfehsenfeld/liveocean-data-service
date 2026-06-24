from django.urls import path
from . import views

urlpatterns = [
    path('forecast/drifters/<str:tracks_filename>-<str:times_filename>',
         views.forecast_drifters, name='forecast-drifters'),

    path('forecast/drifters/<str:tracks_filename>-<str:times_filename>/snapshots',
         views.snapshots, name='forecast-drifters-snapshots'),
]
