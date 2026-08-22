from rest_framework import serializers
from farm_overview.models import IrrigationEvent


class IrrigationEventSerializer(serializers.ModelSerializer):
    zone = serializers.CharField()
    scheduled_at = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField()
    water_liters = serializers.FloatField(required=False, allow_null=True)
    trigger_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(default='scheduled')

    class Meta:
        model = IrrigationEvent
        fields = '__all__'


class IrrigationCreateSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField()

    class Meta:
        model = IrrigationEvent
        fields = '__all__'


class IrrigationOutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    farm_id = serializers.IntegerField()

    class Meta:
        model = IrrigationEvent
        fields = '__all__'