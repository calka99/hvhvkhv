from django.urls import path

from .views import (
    list_categories,
    list_crop_types,
    create_category,
    get_category,
    update_category,
    delete_category,
    list_crops,
    create_crop,
    mark_crop_harvested,
    get_crop,
    update_crop,
    delete_crop,
)

urlpatterns = [
    # Category routes
    path('categories/', list_categories, name='category-list'),
    path('crop-types/', list_crop_types, name='crop-type-list'),
    path('categories/create/', create_category, name='category-create'),
    path('categories/<int:category_id>/', get_category, name='category-detail'),
    path('categories/<int:category_id>/update/', update_category, name='category-update'),
    path('categories/<int:category_id>/delete/', delete_category, name='category-delete'),
    
    # Crop routes
    path('crops/', list_crops, name='crop-list'),
    path('crops/create/', create_crop, name='crop-create'),
    path('crops/<int:crop_id>/harvest/', mark_crop_harvested, name='crop-harvest'),
    path('crops/<int:crop_id>/', get_crop, name='crop-detail'),
    path('crops/<int:crop_id>/update/', update_crop, name='crop-update'),
    path('crops/<int:crop_id>/delete/', delete_crop, name='crop-delete'),
]