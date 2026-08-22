from django.conf import settings
from django.db import models
from django.utils import timezone
from crop_data.models import Crop


class Dashboard(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboards',
    )
    title = models.CharField(max_length=255, default='My Farm Overview')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'dashboards'

    def __str__(self):
        return f"{self.title} ({self.owner})"

    @property
    def farms(self):
        return self.owner.farms.all()

    @property
    def total_farms(self):
        return self.farms.count()

    @property
    def total_active_crops(self):
        return sum(farm.registered_crops.count() for farm in self.farms)

    @property
    def total_pest_alerts(self):
        return sum(farm.pest_alerts.filter(resolved=False).count() for farm in self.farms)

    @property
    def total_livestock(self):
        return sum(farm.livestock.count() for farm in self.farms)

    @property
    def latest_soil_reading(self):
        latest = None
        for farm in self.farms:
            soil = farm.soil_readings.order_by('-recorded_at').first()
            if soil and (latest is None or soil.recorded_at > latest.recorded_at):
                latest = soil
        return latest

    @property
    def latest_weather_log(self):
        latest = None
        for farm in self.farms:
            weather = farm.weather_logs.order_by('-recorded_at').first()
            if weather and (latest is None or weather.recorded_at > latest.recorded_at):
                latest = weather
        return latest

    @property
    def monthly_reports(self):
        from reports.models import MonthlyFarmReport

        return MonthlyFarmReport.objects.filter(farm__owner=self.owner).select_related('farm', 'generated_by')
