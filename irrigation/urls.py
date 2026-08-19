from django.urls import path

from .views import (
    list_irrigation,
    create_irrigation,
    get_irrigation,
    update_irrigation,
    delete_irrigation,
    update_irrigation_status,
)

urlpatterns = [
    # Irrigation routes
    path('', list_irrigation, name='irrigation-list'),
    path('create/', create_irrigation, name='irrigation-create'),
    path('<int:irrigation_id>/', get_irrigation, name='irrigation-detail'),
    path('<int:irrigation_id>/update/', update_irrigation, name='irrigation-update'),
    path('<int:irrigation_id>/delete/', delete_irrigation, name='irrigation-delete'),
    path('<int:irrigation_id>/status/', update_irrigation_status, name='irrigation-status'),
]