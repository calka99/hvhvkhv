from django.contrib import admin
from django.urls import path, include

from .views import (
    create_farm,
    get_farm,
    get_farm_overview,
    list_alerts,
    list_farms,
    list_livestock,
    list_market_prices,
)

urlpatterns = [ 
    path('', list_farms, name='farm-list'),
    path('create/', create_farm, name='farm-create'),
    path('livestock/', list_livestock, name='livestock-list'),
    path('market/', list_market_prices, name='market-list'),
    path('alerts/', list_alerts, name='alert-list'),
    path('<int:farm_id>/', get_farm, name='farm-detail'),
    path('<int:farm_id>/overview/', get_farm_overview, name='farm-overview'),
] 