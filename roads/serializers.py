from django.db import connection
from rest_framework import serializers
from core.myLib.geoModelSerializer import GeoModelSerializer
from .models import Roads

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

class RoadsSerializer(GeoModelSerializer):
    check_geometry_is_valid = True # preveri, če je geometrija veljavna: ne seka sama sebe in je zaprta
    check_st_relation = True # preveri, če se geometrija seka z drugimi geometrijami
    matrix9IM = 'T********' # matrika 9IM za odnos geometrij: 'T********' = notranjost seka
    geoms_as_wkt = True # če je True, serializer pričakuje geometrije v WKT formatu. Če je False, v geojson formatu
    check_st_relation = True # če mora biti nova geometrija preverjena glede na
            # druge geometrije v tabeli glede na matriko9IM. Če ima katera koli geometrija
            # odnos z novo geometrijo, nova geometrija ni shranjena
            # in se sproži napaka pri validaciji, z id-ji geometrij, ki imajo odnos


    class Meta:
        model = Roads
        fields =  ['id', 'geom', 'geom_geojson', 'geom_wkt', 'str_name', 'administrator', 'maintainer', 'length']
                    # da ima model geometrijo \textit{geom}.
                    # dodajte tukaj ostale polja modela, ki jih želite serializirati
                    # in ki niso v GeoModelSerializer

def create(self, validated_data):
    geometry = validated_data.get('geom')
    instance = super().create(validated_data)
    if geometry:
        print(f"Izračunana dolžina (create): {geometry.length}")
        instance.length = geometry.length
        instance.save()
    return instance

def update(self, instance, validated_data):
    geometry = validated_data.get('geom', instance.geom)
    instance = super().update(instance, validated_data)
    if geometry:
        print(f"Izračunana dolžina (update): {geometry.length}")
        instance.length = geometry.length
        instance.save()
    return instance

def validate_geom(self, value):
    """
    Preveri, da linija (cesta) ne seka sama sebe.
    """
    try:
        geom = GEOSGeometry(value.wkt)  # Uporabimo WKT za zanesljivo pretvorbo
    except Exception:
        raise serializers.ValidationError("Neveljavna geometrija.")

    if geom.geom_type != 'LineString':
        raise serializers.ValidationError("Geometrija mora biti tipa LineString.")

    if not geom.simple:
        raise serializers.ValidationError("Linija (cesta) ne sme sekati sama sebe.")

    return value  # vrnemo originalni value, ker bo shranjen v modelu



    