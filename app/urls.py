"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/farms/', include('farm_overview.urls')),
    path('api/crop/', include('crop.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/irrigation/', include('irrigation.urls')),
    path('api/pests/', include('pest_management.urls')),
    path('api/weather/', include('weather.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/accounts/', include('accounts.urls')),
]
