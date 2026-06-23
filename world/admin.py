from django.contrib import admin

from django.contrib.gis import admin
from .models import LiveOceanDrifterForecast, Drifter

admin.site.register(LiveOceanDrifterForecast, admin.ModelAdmin)

admin.site.register(Drifter, admin.ModelAdmin)
