from rest_framework import serializers
from .models import FarmPreference


class FarmPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmPreference
        fields = ['ai_recommendations_enabled']
