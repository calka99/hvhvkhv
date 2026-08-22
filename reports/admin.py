from django.contrib import admin

from .models import MonthlyFarmReport


@admin.register(MonthlyFarmReport)
class MonthlyFarmReportAdmin(admin.ModelAdmin):
	list_display = ('farm', 'month', 'recommendation_status', 'generated_at', 'generated_by')
	list_filter = ('month', 'recommendation_status')
	search_fields = ('farm__name', 'ai_recommendation')
	readonly_fields = ('generated_at', 'generated_by')
