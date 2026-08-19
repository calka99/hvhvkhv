from django.urls import path

from .views import get_settings, update_settings

urlpatterns = [
    path('<int:farm_id>/', get_settings, name='settings-detail'),
    path('<int:farm_id>/update/', update_settings, name='settings-update'),
]