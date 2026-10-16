from rest_framework import serializers

from farm_overview.models import Livestock, LivestockHealthAlert
from .models import LivestockType


class LivestockTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LivestockType
        fields = ["id", "name"]


class LivestockSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)

    class Meta:
        model = Livestock
        fields = [
            'id',
            'farm',
            'farm_name',
            'species',
            'tag_id',
            'count',
            'health_status',
            'last_vaccination',
            'feeding_schedule',
            'productivity_metric',
        ]
        read_only_fields = ['id', 'farm']

    def validate_count(self, value):
        if value < 0:
            raise serializers.ValidationError('Count cannot be negative.')
        return value


class LivestockHealthAlertSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    livestock_name = serializers.CharField(source='livestock.species', read_only=True)

    class Meta:
        model = LivestockHealthAlert
        fields = [
            'id',
            'farm',
            'farm_name',
            'livestock',
            'livestock_name',
            'disease_name',
            'severity',
            'detected_at',
            'recommended_action',
            'resolved',
        ]
        read_only_fields = ['id', 'farm', 'livestock']
