from django.urls import path

from .views import get_settings, update_settings

urlpatterns = [
    path('', get_settings, name='settings-detail'),
    path('update/', update_settings, name='settings-update'),
]