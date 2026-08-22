from rest_framework import serializers

from farm_overview.models import SoilReading


class SoilReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilReading
        fields = [
            'id',
            'farm',
            'recorded_at',
            'moisture_pct',
            'ph_level',
            'nitrogen_ppm',
            'phosphorus_ppm',
            'potassium_ppm',
            'organic_matter_pct',
            'degradation_risk',
        ]
        read_only_fields = ['id', 'farm']

    def validate_moisture_pct(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError('Moisture must be between 0 and 100 percent.')
        return value

    def validate_ph_level(self, value):
        if not 0 <= value <= 14:
            raise serializers.ValidationError('pH must be between 0 and 14.')
        return value
