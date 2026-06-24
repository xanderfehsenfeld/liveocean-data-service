from django.contrib import admin

from django.contrib.gis import admin
from .models import LiveOceanDrifterForecast, Drifter, DrifterSnapshot

admin.site.register(LiveOceanDrifterForecast, admin.ModelAdmin)
