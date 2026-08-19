from rest_framework import serializers
from farm_overview.models import Settings


class SettingsSerializer(serializers.ModelSerializer):
    notifications_enabled = serializers.BooleanField(required=False)
    ai_recommendations_enabled = serializers.BooleanField(required=False)
    sms_alerts_enabled = serializers.BooleanField(required=False)
    data_sync_interval_minutes = serializers.IntegerField(required=False)
    connected_devices = serializers.IntegerField(required=False)
    language = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Settings
        fields = '__all__'


class SettingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = [
            'notifications_enabled',
            'ai_recommendations_enabled',
            'sms_alerts_enabled',
            'data_sync_interval_minutes',
            'connected_devices',
            'language',
        ]
