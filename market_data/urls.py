from django.urls import path

from .views import market_prices

urlpatterns = [
    path('', market_prices, name='market-prices'),
]
