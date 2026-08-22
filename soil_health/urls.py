from django.urls import path

from .views import soil_readings

urlpatterns = [
    path('', soil_readings, name='soil-readings'),
]