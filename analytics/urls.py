from django.urls import path

from .views import (
    list_analytics,
    create_analytics,
    get_analytics,
    update_analytics,
    delete_analytics,
)

urlpatterns = [
    # Analytics routes
    path('', list_analytics, name='analytics-list'),
    path('create/', create_analytics, name='analytics-create'),
    path('<int:analytics_id>/', get_analytics, name='analytics-detail'),
    path('<int:analytics_id>/update/', update_analytics, name='analytics-update'),
    path('<int:analytics_id>/delete/', delete_analytics, name='analytics-delete'),
]
