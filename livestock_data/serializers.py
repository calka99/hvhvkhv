from rest_framework import serializers

from farm_overview.models import Livestock


class LivestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livestock
        fields = [
            'id',
            'farm',
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
