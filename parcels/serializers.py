from django.db import connection
from rest_framework import serializers
from core.myLib.geoModelSerializer import GeoModelSerializer
from .models import Parcels, Parcels_Owners 
from djangoapi.settings import ST_SNAP_PRECISION

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

class ParcelsSerializer(GeoModelSerializer):
    check_geometry_is_valid = True # preveri, če je geometrija veljavna: ne seka sama sebe in je zaprta
    check_st_relation = True # preveri, če se geometrija seka z drugimi geometrijami
    matrix9IM = 'T********' # matrika 9IM za odnos geometrij: 'T********' = notranjost seka
    geoms_as_wkt = True # če je True, serializer pričakuje geometrije v WKT formatu. Če je False, v geojson formatu
    check_st_relation = True # če mora biti nova geometrija preverjena glede na
            # druge geometrije v tabeli glede na matriko9IM. Če ima katera koli geometrija
            # odnos z novo geometrijo, nova geometrija ni shranjena
            # in se sproži napaka pri validaciji, z id-ji geometrij, ki imajo odnos

    class Meta:
        model = Parcels
        fields = GeoModelSerializer.Meta.fields + ['parc_st', 'sifko', 'area'] #  Serializer predpostavlja, 
                    # da ima model geometrijo \textit{geom}.
                    # dodajte tukaj ostale polja modela, ki jih želite serializirati
                    # in ki niso v GeoModelSerializer

    


def validate_geom(self, value):
    print('🔍 validate_geom, child: preverjam veljavnost geometrije')

    # Poskusi pretvoriti string v geometrijski objekt
    try:
        geom = GEOSGeometry(value)
    except Exception as e:
        raise serializers.ValidationError(f"❌ Napaka pri parsiranju geometrije: {e}")

    # 1. Preveri, ali je veljavna
    if not geom.valid:
        raise serializers.ValidationError("❌ Geometrija ni veljavna (morda seka samo sebe ali ni zaprta).")

    # 2. Preveri, ali seka druge parcele (razen sebe)
    conflicting_parcels = Parcels.objects.filter(geom__intersects=geom).exclude(id=self.instance.id if self.instance else None)

    if conflicting_parcels.exists():
        conflicting_ids = conflicting_parcels.values_list('id', flat=True)
        raise serializers.ValidationError({"ok": False, "message": f"Geometrija se seka z obstoječimi parcelami: {conflicting_ids}"})
        
    self.area = geom.area
    return geom

def update(self, instance, validated_data):
    if 'geom' in validated_data and hasattr(self, 'area'):
        validated_data['area'] = self.area
    return super().update(instance, validated_data)
        
class ParcelsOwnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcels_Owners
        fields = ['id', 'name', 'dni']
    
    def validate_name(self, value):
        if 'bad' in value:
            raise serializers.ValidationError("The name can't contain 'bad'.")
        return value   