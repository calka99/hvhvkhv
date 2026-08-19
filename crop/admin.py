from django.contrib import admin

from .models import Category, Crop


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "description")

