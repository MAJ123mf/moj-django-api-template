from django.db import models
from django.contrib.gis.db import models as gis_models
from djangoapi.settings import EPSG_FOR_GEOMETRIES
from django.core.validators import MinValueValidator, MaxValueValidator

class Parcels(models.Model):
    id = models.AutoField(primary_key=True)
    parc_st = models.CharField(max_length=10, blank=True, null=True)
    sifko=models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ]
    )
    area = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    geom = gis_models.PolygonField(srid=int(EPSG_FOR_GEOMETRIES), blank=True, null=True)


class Parcels_Owners(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)#optional
    dni = models.CharField(max_length=100, unique=True)#mandatory and unique