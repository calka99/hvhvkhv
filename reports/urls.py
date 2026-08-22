from django.urls import path

from .views import generate_monthly_reports, list_monthly_reports, update_monthly_report

urlpatterns = [
    path('monthly/', list_monthly_reports, name='monthly-report-list'),
    path('monthly/generate/', generate_monthly_reports, name='monthly-report-generate'),
    path('monthly/<int:report_id>/', update_monthly_report, name='monthly-report-update'),
]
