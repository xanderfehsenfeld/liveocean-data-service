from django.urls import path
from . import views

urlpatterns = [
    path('forecast/drifters/<str:tracks_filename>-<str:times_filename>',
         views.forecast_drifters, name='forecast-drifters'),
    # path('worldborders/<int:pk>/', views.worldborder_detail, name='worldborder-detail'),
]
