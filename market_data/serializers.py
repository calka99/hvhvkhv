from rest_framework import serializers

from farm_overview.models import MarketPrice


class MarketPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketPrice
        fields = [
            'id',
            'commodity',
            'region',
            'price_per_kg',
            'currency',
            'trend',
            'recorded_at',
            'demand_level',
        ]
        read_only_fields = ['id']

    def validate_price_per_kg(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value
