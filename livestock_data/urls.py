from django.urls import path

from .views import livestock_record_detail, livestock_records, livestock_health_alerts, livestock_types

urlpatterns = [
    path('types/', livestock_types, name='livestock-type-list'),
    path('<int:livestock_id>/', livestock_record_detail, name='livestock-record-detail'),
    path('', livestock_records, name='livestock-records'),
    path('health-alerts/', livestock_health_alerts, name='livestock-health-alerts'),
]
