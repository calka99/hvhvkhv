from rest_framework import serializers
from .models import Category, Crop


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CropSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    variety = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    growth_stage = serializers.CharField(default='seedling')
    planting_date = serializers.DateTimeField()
    expected_harvest_date = serializers.DateTimeField(required=False, allow_null=True)
    planting_density = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    area_hectares = serializers.FloatField(default=0.0)
    historical_yield_kg = serializers.FloatField(required=False, allow_null=True)
    ai_recommendation = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Crop
        fields = '__all__'


class CropCreateSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField()

    class Meta:
        model = Crop
        fields = '__all__'


class CropOutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    farm_id = serializers.IntegerField()

    class Meta:
        model = Crop
        fields = '__all__'
