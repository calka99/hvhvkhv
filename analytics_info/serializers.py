from rest_framework import serializers
from farm_overview.models import AnalyticsSnapshot


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    period_label = serializers.CharField()
    crop_yield_kg = serializers.FloatField()
    water_consumption_liters = serializers.FloatField()
    resource_efficiency_pct = serializers.FloatField()
    production_cost = serializers.FloatField()
    revenue = serializers.FloatField()
    sustainability_score = serializers.FloatField()

    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'


class AnalyticsCreateSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField()

    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'


class AnalyticsOutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    farm_id = serializers.IntegerField()

    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'
