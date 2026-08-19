from django.urls import path

from .views import (
    list_pest_alerts,
    create_pest_alert,
    get_pest_alert,
    update_pest_alert,
    delete_pest_alert,
    resolve_pest_alert,
)

urlpatterns = [
    # Pest Alert routes
    path('', list_pest_alerts, name='pest-alert-list'),
    path('create/', create_pest_alert, name='pest-alert-create'),
    path('<int:pest_alert_id>/', get_pest_alert, name='pest-alert-detail'),
    path('<int:pest_alert_id>/update/', update_pest_alert, name='pest-alert-update'),
    path('<int:pest_alert_id>/delete/', delete_pest_alert, name='pest-alert-delete'),
    path('<int:pest_alert_id>/resolve/', resolve_pest_alert, name='pest-alert-resolve'),
]