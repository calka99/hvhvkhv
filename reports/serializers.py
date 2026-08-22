from rest_framework import serializers

from .models import MonthlyFarmReport


class MonthlyFarmReportSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)

    class Meta:
        model = MonthlyFarmReport
        fields = [
            'id',
            'farm',
            'farm_name',
            'month',
            'activity_data',
            'ai_recommendation',
            'recommendation_status',
            'generated_at',
            'generated_by',
        ]
        read_only_fields = [
            'id',
            'farm_name',
            'month',
            'activity_data',
            'generated_at',
            'generated_by',
        ]
