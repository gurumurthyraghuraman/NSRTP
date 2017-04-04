from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField

class nsrpt(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

class networkconnection(models.Model):
    networkid = models.TextField()
    LatLong = models.PointField()
    ConnectedPoints = ArrayField(models.BigIntegerField())

class networkconn(models.Model):
    networkid = models.TextField()
    LatLongId = models.BigIntegerField()
    Lat = models.FloatField()
    Long = models.FloatField()
    LatLongx = models.FloatField(null=True)
    LatLongy = models.FloatField(null=True)
    ConnectedPoints = ArrayField(models.BigIntegerField())

class graphdata(models.Model):
    graphname = models.TextField()
    graphid = models.TextField()
    datestamp = models.DateField(auto_now_add=True, blank=True)
    timestamp = models.TimeField(auto_now_add=True, blank=True)
