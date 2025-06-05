from django.db import models
from django.contrib.gis.db import models as gis_models
from djangoapi.settings import EPSG_FOR_GEOMETRIES
# Create your models here.
class Roads(models.Model):
    id = models.AutoField(primary_key=True)
    str_name = models.CharField(max_length=100, blank=True, null=True)
    administrator = models.CharField(max_length=64, blank=True, null=True)
    maintainer = models.CharField(max_length=64, blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    geom = gis_models.LineStringField(srid=int(EPSG_FOR_GEOMETRIES), blank=True, null=True)  # občutljivo na velike in male črke


