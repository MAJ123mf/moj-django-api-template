from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
#router.register(r'core', views.BuildingsModelViewSet)

urlpatterns = [
    path("hello_world/", views.HelloWord.as_view(),name="hello_world"),
    path('', include(router.urls)),
    path('not_loggedin/', views.notLoggedIn, name="not_loggedin"),
    path('login/', views.LoginView.as_view(),name="login"),
    path('logout/', views.LogoutView.as_view(),name="login"),
    path('isloggedin/', views.IsLoggedIn.as_view(),name="isloggedin"),
]