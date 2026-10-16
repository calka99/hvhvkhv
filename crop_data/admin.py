from django.contrib import admin

from .models import Category, Crop, CropType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "lifespan_days", "created_at")
    search_fields = ("name",)


@admin.register(CropType)
class CropTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "lifespan_days", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "category__name")


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "crop_type", "category", "price", "stock", "created_at")
    list_filter = ("crop_type", "category")
    search_fields = ("name", "description")

