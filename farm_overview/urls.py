from django.contrib import admin
from django.urls import path, include

from .views import create_farm, get_farm, get_farm_overview, list_farms

urlpatterns = [ 
    path('', list_farms, name='farm-list'),
    path('create/', create_farm, name='farm-create'),
    path('<int:farm_id>/', get_farm, name='farm-detail'),
    path('<int:farm_id>/overview/', get_farm_overview, name='farm-overview'),
] 