from rest_framework import serializers
from farm_overview.models import PestAlert


class PestAlertSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    crop_name = serializers.CharField()
    pest_or_disease = serializers.CharField()
    risk_level = serializers.CharField(default='low')
    detected_at = serializers.DateTimeField()
    detection_method = serializers.CharField(default='image_recognition')
    recommended_action = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    resolved = serializers.BooleanField(default=False)

    class Meta:
        model = PestAlert
        fields = '__all__'
        read_only_fields = ['farm']


class PestAlertCreateSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField()

    class Meta:
        model = PestAlert
        fields = '__all__'


class PestAlertOutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    farm_id = serializers.IntegerField()

    class Meta:
        model = PestAlert
        fields = '__all__'