from django.urls import path

from .views import me, update_profile

urlpatterns = [
    path('me/', me, name='account-me'),
    path('me/update/', update_profile, name='account-update'),
]
