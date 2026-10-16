from django.contrib import admin
from django.urls import path, include

from .views import (
    create_farm,
    delete_farm,
    get_farm,
    get_farm_overview,
    list_owned_farms,
    list_alerts,
    list_farms,
    list_livestock,
    list_market_prices,
    update_farm,
)

urlpatterns = [ 
    path('', list_farms, name='farm-list'),
    path('mine/', list_owned_farms, name='farm-owned-list'),
    path('create/', create_farm, name='farm-create'),
    path('<int:farm_id>/update/', update_farm, name='farm-update'),
    path('<int:farm_id>/delete/', delete_farm, name='farm-delete'),
    path('livestock/', list_livestock, name='livestock-list'),
    path('market/', list_market_prices, name='market-list'),
    path('alerts/', list_alerts, name='alert-list'),
    path('<int:farm_id>/', get_farm, name='farm-detail'),
    path('<int:farm_id>/overview/', get_farm_overview, name='farm-overview'),
] 