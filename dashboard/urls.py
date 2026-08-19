from django.urls import path

from .views import dashboard_overview

urlpatterns = [
    path('overview/', dashboard_overview, name='dashboard-overview'),
]