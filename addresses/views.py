from django.http import JsonResponse
from django.views import View 
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import AddressSerializer
from .models import Addresses

#rest_framework imports
from rest_framework import viewsets
from rest_framework import permissions

#My imports
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION, MAX_NUMBER_OF_RETRIEVED_ROWS
from core.myLib.baseDjangoView import BaseDjangoView


class HelloWord(View):
    def get(self, request):
        return JsonResponse({"ok":True,"message": "Hello world from app. Addresses", "data":[]})

# Create your views here.
class AddressesModelViewSet(viewsets.ModelViewSet):
    #     GET operation over /addresses/addresses/. It will return all reccords
    #     GET operation over /addresses/addresses/<id>/. 
    #     POST operation over /addresses/addresses/. It will insert a new record
    #     PUT operation over /addresses/addresses/<id>/. 
    #     PATCH operation over /addresses/addresses/<id>/. 
    #     DELETE operation over /addresses/addresses/<id>/. 
    queryset = Addresses.objects.all().order_by('id')  # To je SORT:  izpis na front-endu bo urejen po id
    serializer_class = AddressSerializer           
    permission_classes = [permissions.AllowAny]     # izpis na front-endu bo urejen po id-ju
                                
