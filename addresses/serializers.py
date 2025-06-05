from django.db import connection
from rest_framework import serializers
from core.myLib.geoModelSerializer import GeoModelSerializer
from .models import Addresses

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView


class AddressSerializer(GeoModelSerializer):
    class Meta:
        model = Addresses
        fields = ['id','building_num', 'street', 'house_num', 'post_num', 'post_name', 'geom', 'geom_geojson', 'geom_wkt',]



