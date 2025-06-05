from django.contrib import admin
from django.contrib.gis import admin
from .models import Parcels, Parcels_Owners

admin.site.register(Parcels_Owners, admin.ModelAdmin)
admin.site.register(Parcels, admin.GISModelAdmin)
