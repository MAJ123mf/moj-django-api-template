from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'roads', views.RoadsModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(),name="hello_world"),  # http://localhost:8000/roads/roads/
    path('', include(router.urls)),    
    path('roads_view/<str:action>/', views.RoadsView.as_view(), name='roads_views'),  # http://localhost:8000/roads/roads_view/selectall/
    path('roadls_view/<str:action>/<int:id>/', views.RoadsView.as_view(), name='roads_views'),  # http://localhost:8000/roads/roads_view/selectone/1/                                    
]
                                    

