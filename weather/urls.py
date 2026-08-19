from django.urls import path

from .views import (
    list_weather,
    create_weather,
    get_weather,
    update_weather,
    delete_weather,
)

urlpatterns = [
    # Weather routes
    path('', list_weather, name='weather-list'),
    path('create/', create_weather, name='weather-create'),
    path('<int:weather_id>/', get_weather, name='weather-detail'),
    path('<int:weather_id>/update/', update_weather, name='weather-update'),
    path('<int:weather_id>/delete/', delete_weather, name='weather-delete'),
]