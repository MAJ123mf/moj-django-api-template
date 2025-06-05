from django.contrib import admin
from django.contrib.gis import admin
from .models import Addresses

admin.site.register(Addresses, admin.GISModelAdmin)

# Register your models here.
