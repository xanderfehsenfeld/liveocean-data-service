from django.contrib.gis.db import models


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
    drifterData = models.JSONField("JSON Response")
    times = models.JSONField("Times")


class Drifter(models.Model):
    location = models.PointField("location")
    forecast = models.ForeignKey(LiveOceanDrifterForecast, on_delete=models.CASCADE)
    timestamp = models.TimeField("Time")
    drifter_id = models.IntegerField("ID within forecast")


    