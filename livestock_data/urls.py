from django.urls import path

from .views import livestock_records

urlpatterns = [
    path('', livestock_records, name='livestock-records'),
]
