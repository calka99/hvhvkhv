from django.urls import path

from .views import (
    list_weather,
    next_hour_weather,
    next_24_hours_weather,
    create_weather,
    get_weather,
    update_weather,
    delete_weather,
)

urlpatterns = [
    # Weather routes
    path('', list_weather, name='weather-list'),
    path('next-hour/', next_hour_weather, name='weather-next-hour'),
    path('next-24-hours/', next_24_hours_weather, name='weather-next-24-hours'),
    path('create/', create_weather, name='weather-create'),
    path('<int:weather_id>/', get_weather, name='weather-detail'),
    path('<int:weather_id>/update/', update_weather, name='weather-update'),
    path('<int:weather_id>/delete/', delete_weather, name='weather-delete'),
]