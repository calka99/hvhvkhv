from rest_framework import serializers
from django.utils import timezone
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
        read_only_fields = ['farm', 'completed_at']

    def create(self, validated_data):
        if validated_data.get('status') == 'completed':
            validated_data['completed_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)
        if new_status == 'completed' and instance.status != 'completed':
            validated_data['completed_at'] = timezone.now()
        elif new_status != 'completed':
            validated_data['completed_at'] = None
        return super().update(instance, validated_data)


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