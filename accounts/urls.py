from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import login, logout, me, register, update_profile

urlpatterns = [
    path('register/', register, name='account-register'),
    path('login/', login, name='account-login'),
    path('refresh/', TokenRefreshView.as_view(), name='account-refresh'),
    path('logout/', logout, name='account-logout'),
    path('me/', me, name='account-me'),
    path('me/update/', update_profile, name='account-update'),
]
