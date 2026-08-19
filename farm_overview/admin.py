from django.contrib import admin
from .models import (
    Farm,
    Crop,
    SoilReading,
    WeatherLog,
    IrrigationEvent,
    PestAlert,
    Livestock,
    MarketPrice,
    AnalyticsSnapshot,
    Report,
    Alert,
    Settings,
)


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'size_hectares', 'farm_type', 'created_at')
    list_filter = ('farm_type', 'created_at')
    search_fields = ('name', 'location', 'owner__username')
    readonly_fields = ('created_at',)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'variety', 'growth_stage', 'planting_date', 'area_hectares')
    list_filter = ('growth_stage', 'farm', 'planting_date')
    search_fields = ('name', 'variety', 'farm__name')
    readonly_fields = ()


@admin.register(SoilReading)
class SoilReadingAdmin(admin.ModelAdmin):
    list_display = ('farm', 'recorded_at', 'moisture_pct', 'ph_level', 'degradation_risk')
    list_filter = ('farm', 'recorded_at', 'degradation_risk')
    search_fields = ('farm__name',)
    readonly_fields = ('recorded_at',)


@admin.register(WeatherLog)
class WeatherLogAdmin(admin.ModelAdmin):
    list_display = ('farm', 'recorded_at', 'temperature_c', 'humidity_pct', 'rainfall_mm')
    list_filter = ('farm', 'recorded_at')
    search_fields = ('farm__name',)
    readonly_fields = ('recorded_at',)


@admin.register(IrrigationEvent)
class IrrigationEventAdmin(admin.ModelAdmin):
    list_display = ('farm', 'zone', 'scheduled_at', 'duration_minutes', 'status')
    list_filter = ('farm', 'status', 'scheduled_at')
    search_fields = ('farm__name', 'zone')


@admin.register(PestAlert)
class PestAlertAdmin(admin.ModelAdmin):
    list_display = ('crop_name', 'farm', 'pest_or_disease', 'risk_level', 'detected_at', 'resolved')
    list_filter = ('farm', 'risk_level', 'resolved', 'detected_at')
    search_fields = ('crop_name', 'pest_or_disease', 'farm__name')
    readonly_fields = ('detected_at',)


@admin.register(Livestock)
class LivestockAdmin(admin.ModelAdmin):
    list_display = ('farm', 'species', 'count', 'health_status', 'tag_id')
    list_filter = ('farm', 'species', 'health_status')
    search_fields = ('farm__name', 'species', 'tag_id')


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ('commodity', 'region', 'price_per_kg', 'currency', 'trend', 'recorded_at')
    list_filter = ('commodity', 'region', 'trend', 'recorded_at')
    search_fields = ('commodity', 'region')
    readonly_fields = ('recorded_at',)


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('farm', 'period_label', 'crop_yield_kg', 'revenue', 'sustainability_score')
    list_filter = ('farm', 'period_label')
    search_fields = ('farm__name', 'period_label')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'farm', 'report_type', 'period_label', 'generated_at')
    list_filter = ('farm', 'report_type', 'generated_at')
    search_fields = ('title', 'farm__name')
    readonly_fields = ('generated_at',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('category', 'farm', 'severity', 'message', 'created_at', 'acknowledged')
    list_filter = ('farm', 'severity', 'category', 'created_at', 'acknowledged')
    search_fields = ('message', 'farm__name', 'category')
    readonly_fields = ('created_at',)


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('farm', 'notifications_enabled', 'ai_recommendations_enabled', 'language')
    list_filter = ('farm', 'notifications_enabled', 'ai_recommendations_enabled')
    search_fields = ('farm__name', 'language')
