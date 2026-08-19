from django.conf import settings
from django.db import models
from django.utils import timezone


class Farm(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farms',
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    size_hectares = models.FloatField()
    farm_type = models.CharField(max_length=50, default="mixed")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Crop(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="overview_crops")
    name = models.CharField(max_length=255)
    variety = models.CharField(max_length=255, blank=True, null=True)
    growth_stage = models.CharField(max_length=100, default="seedling")
    planting_date = models.DateTimeField()
    expected_harvest_date = models.DateTimeField(blank=True, null=True)
    planting_density = models.CharField(max_length=100, blank=True, null=True)
    area_hectares = models.FloatField(default=0.0)
    historical_yield_kg = models.FloatField(blank=True, null=True)
    ai_recommendation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.farm.name})"


class SoilReading(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="soil_readings")
    recorded_at = models.DateTimeField(default=timezone.now)
    moisture_pct = models.FloatField()
    ph_level = models.FloatField()
    nitrogen_ppm = models.FloatField(blank=True, null=True)
    phosphorus_ppm = models.FloatField(blank=True, null=True)
    potassium_ppm = models.FloatField(blank=True, null=True)
    organic_matter_pct = models.FloatField(blank=True, null=True)
    degradation_risk = models.CharField(max_length=50, default="low")

    def __str__(self):
        return f"Soil reading for {self.farm.name} at {self.recorded_at}"


class WeatherLog(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="weather_logs")
    recorded_at = models.DateTimeField(default=timezone.now)
    temperature_c = models.FloatField()
    humidity_pct = models.FloatField()
    rainfall_mm = models.FloatField(default=0.0)
    wind_kph = models.FloatField(default=0.0)
    forecast_summary = models.CharField(max_length=255, blank=True, null=True)
    recommended_action = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Weather log for {self.farm.name} on {self.recorded_at}"


class IrrigationEvent(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="irrigation_events")
    zone = models.CharField(max_length=100)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    water_liters = models.FloatField(blank=True, null=True)
    trigger_reason = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default="scheduled")

    def __str__(self):
        return f"Irrigation event for {self.farm.name} in {self.zone}"


class PestAlert(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="pest_alerts")
    crop_name = models.CharField(max_length=255)
    pest_or_disease = models.CharField(max_length=255)
    risk_level = models.CharField(max_length=50, default="low")
    detected_at = models.DateTimeField(default=timezone.now)
    detection_method = models.CharField(max_length=100, default="image_recognition")
    recommended_action = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Pest alert for {self.crop_name} ({self.farm.name})"


class Livestock(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="livestock")
    species = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255, blank=True, null=True)
    count = models.IntegerField(default=1)
    health_status = models.CharField(max_length=100, default="healthy")
    last_vaccination = models.DateTimeField(blank=True, null=True)
    feeding_schedule = models.CharField(max_length=255, blank=True, null=True)
    productivity_metric = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.count} x {self.species} on {self.farm.name}"


class MarketPrice(models.Model):
    commodity = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    price_per_kg = models.FloatField()
    currency = models.CharField(max_length=20, default="NGN")
    trend = models.CharField(max_length=50, default="stable")
    recorded_at = models.DateTimeField(default=timezone.now)
    demand_level = models.CharField(max_length=50, default="medium")

    def __str__(self):
        return f"{self.commodity} price in {self.region}"


class AnalyticsSnapshot(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="analytics_snapshots")
    period_label = models.CharField(max_length=100)
    crop_yield_kg = models.FloatField(default=0.0)
    water_consumption_liters = models.FloatField(default=0.0)
    resource_efficiency_pct = models.FloatField(default=0.0)
    production_cost = models.FloatField(default=0.0)
    revenue = models.FloatField(default=0.0)
    sustainability_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"Analytics snapshot for {self.farm.name}: {self.period_label}"


class Report(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="reports")
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=100, default="production")
    period_label = models.CharField(max_length=100, blank=True, null=True)
    generated_at = models.DateTimeField(default=timezone.now)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} for {self.farm.name}"


class Alert(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="alerts")
    category = models.CharField(max_length=100)
    severity = models.CharField(max_length=50, default="info")
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.severity.upper()} alert for {self.farm.name}"


class Settings(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="settings")
    notifications_enabled = models.BooleanField(default=True)
    ai_recommendations_enabled = models.BooleanField(default=True)
    sms_alerts_enabled = models.BooleanField(default=False)
    data_sync_interval_minutes = models.IntegerField(default=15)
    connected_devices = models.IntegerField(default=0)
    language = models.CharField(max_length=20, default="en")

    class Meta:
        verbose_name_plural = "settings"

    def __str__(self):
        return f"Settings for {self.farm.name}"

