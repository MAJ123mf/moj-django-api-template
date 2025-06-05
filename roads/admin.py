from django.contrib import admin
from django.contrib.gis import admin
from .models import Roads

admin.site.register(Roads, admin.GISModelAdmin) 
