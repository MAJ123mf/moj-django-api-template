"""
URL configuration for djangoapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.views import custom_logout_view

schema_view = get_schema_view(
   openapi.Info(
      title="Universitat Politècnica de València",
      default_version='v1',
      description="Django API template",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="joamona@cgf.upv.es"),
      license=openapi.License(name="GPL License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),   # http://localhost:8000/swagger.json
    path('swagger/', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),   # http://localhost:8000/swagger/
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),   # http://localhost:8000/redoc/

    path('admin/', admin.site.urls),  # http://localhost:8000/admin/
    path("accounts/logout/", custom_logout_view, name="logout"),  # http://localhost:8000/accounts/logout/
    path("accounts/login/", include("django.contrib.auth.urls")),  # http://localhost:8000/accounts/login/
    path("accounts/", include("django.contrib.auth.urls")),         # http://localhost:8000/accounts/
    path("api-auth/", include("rest_framework.urls")),               # http://localhost:8000/api-auth/

    path('codelist/', include('codelist.urls')),
    path('core/', include('core.urls')),
    path('buildings/', include('buildings.urls')),
    path('flowers/', include('flowers.urls')),
    path('smartcities/', include('smartcities.urls')),
    path('parcels/', include('parcels.urls')),
    path('roads/', include('roads.urls')),
    path('addresses/', include('addresses.urls'))
]
