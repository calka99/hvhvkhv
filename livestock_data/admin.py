from django.contrib import admin
from .models import LivestockType


@admin.register(LivestockType)
class LivestockTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
