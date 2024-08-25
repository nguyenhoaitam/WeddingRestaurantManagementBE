from django.urls import path, include
from rest_framework import routers
from weddingrestaurant import views

r = routers.DefaultRouter()

r.register('users', views.UserViewSet, 'users')

urlpatterns = [
    path('', include(r.urls))
]
