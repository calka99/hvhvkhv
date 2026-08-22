from rest_framework import serializers

from dashboard.models import Dashboard
from farm_overview.serializers import FarmSerializer, SoilReadingSerializer, WeatherLogSerializer
from reports.serializers import MonthlyFarmReportSerializer


class DashboardSerializer(serializers.ModelSerializer):
    farms = FarmSerializer(many=True, read_only=True, source='owner.farms')
    total_farms = serializers.SerializerMethodField()
    total_active_crops = serializers.SerializerMethodField()
    total_pest_alerts = serializers.SerializerMethodField()
    total_livestock = serializers.SerializerMethodField()
    latest_soil_reading = serializers.SerializerMethodField()
    latest_weather_log = serializers.SerializerMethodField()
    monthly_reports = serializers.SerializerMethodField()

    class Meta:
        model = Dashboard
        fields = [
            'id',
            'title',
            'owner',
            'created_at',
            'updated_at',
            'farms',
            'total_farms',
            'total_active_crops',
            'total_pest_alerts',
            'total_livestock',
            'latest_soil_reading',
            'latest_weather_log',
            'monthly_reports',
        ]

    def get_total_farms(self, obj):
        return obj.total_farms

    def get_total_active_crops(self, obj):
        return obj.total_active_crops

    def get_total_pest_alerts(self, obj):
        return obj.total_pest_alerts

    def get_total_livestock(self, obj):
        return obj.total_livestock

    def get_latest_soil_reading(self, obj):
        latest = obj.latest_soil_reading
        return SoilReadingSerializer(latest).data if latest else None

    def get_latest_weather_log(self, obj):
        latest = obj.latest_weather_log
        return WeatherLogSerializer(latest).data if latest else None

    def get_monthly_reports(self, obj):
        return MonthlyFarmReportSerializer(obj.monthly_reports, many=True).data
