from django.contrib.gis import admin
from .models import nsrpt

admin.site.register(nsrpt, admin.GeoModelAdmin)