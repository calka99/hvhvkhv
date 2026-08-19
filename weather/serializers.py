from rest_framework import serializers
from farm_overview.models import WeatherLog


class WeatherLogSerializer(serializers.ModelSerializer):
    temperature_c = serializers.FloatField()
    humidity_pct = serializers.FloatField()
    rainfall_mm = serializers.FloatField(default=0.0)
    wind_kph = serializers.FloatField(default=0.0)
    forecast_summary = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recommended_action = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recorded_at = serializers.DateTimeField()

    class Meta:
        model = WeatherLog
        fields = '__all__'


class WeatherCreateSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField()

    class Meta:
        model = WeatherLog
        fields = '__all__'


class WeatherOutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    farm_id = serializers.IntegerField()

    class Meta:
        model = WeatherLog
        fields = '__all__'