from rest_framework import serializers
from .models import (
    Alert,
    AnalyticsSnapshot,
    Farm,
    IrrigationEvent,
    Livestock,
    MarketPrice,
    PestAlert,
    Report,
    Settings,
    SoilReading,
    WeatherLog,
)


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'


class FarmCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ['name', 'location', 'size_hectares', 'farm_type']


class FarmOutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Farm
        fields = '__all__'


class SoilReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilReading
        fields = '__all__'


class WeatherLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherLog
        fields = '__all__'


class IrrigationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrrigationEvent
        fields = '__all__'


class PestAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PestAlert
        fields = '__all__'


class LivestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livestock
        fields = '__all__'


class MarketPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketPrice
        fields = '__all__'


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'


class FarmOverviewSerializer(serializers.Serializer):
    farm = FarmSerializer()
    active_crops = serializers.IntegerField()
    total_crop_yield_kg = serializers.FloatField()
    open_pest_alerts = serializers.IntegerField()
    livestock_count = serializers.IntegerField()
    latest_soil = SoilReadingSerializer(allow_null=True)
    latest_weather = WeatherLogSerializer(allow_null=True)
    upcoming_irrigation = IrrigationEventSerializer(many=True)
    recent_alerts = AlertSerializer(many=True)
