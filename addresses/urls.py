from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'addresses', views.AddressesModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(),name="hello_world"),  # http://localhost:8000/addresses/addresses/
    path('', include(router.urls)),                                        
]
