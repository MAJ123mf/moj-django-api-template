from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'parcels', views.ParcelsModelViewSet)
router.register(r'parcelsowners', views.ParcelOwnersModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(),name="hello_world"),  # http://localhost:8000/parcels/hello_world/
    # path("parcels/", views.ParcelsView.as_view(), name="parcels"),  # http://localhost:8000/parcels/parcels/
    path('', include(router.urls)),    
    path('parcels_view/<str:action>/', views.ParcelsView.as_view(), name='parcels_views'),  # http://localhost:8000/parcels/parcels_view/selectall/
    path('parcels_view/<str:action>/<int:id>/', views.ParcelsView.as_view(), name='parcels_views'),  # http://localhost:8000/parcels/parcels_view/selectone/1/                                    
]

