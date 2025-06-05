from django.db import models
from django.contrib.gis.db import models as gis_models
from djangoapi.settings import EPSG_FOR_GEOMETRIES
# Create your models here.
class Addresses(models.Model):
    id = models.AutoField(primary_key=True)
    building_num = models.IntegerField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    house_num = models.CharField(max_length=8, blank=True, null=True)
    post_num = models.IntegerField(blank=True, null=True)
    post_name = models.CharField(max_length=64, blank=True, null=True)
    geom = gis_models.PointField(srid=int(EPSG_FOR_GEOMETRIES), blank=True, null=True)
