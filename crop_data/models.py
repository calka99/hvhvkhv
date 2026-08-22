from django.db import models
from farm_overview.models import Farm


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Crop(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="registered_crops")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="crops")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    variety = models.CharField(max_length=255, blank=True, null=True)
    growth_stage = models.CharField(max_length=100, default="seedling")
    planting_date = models.DateTimeField(null=True, blank=True)
    expected_harvest_date = models.DateTimeField(blank=True, null=True)
    planting_density = models.CharField(max_length=100, blank=True, null=True)
    area_hectares = models.FloatField(default=0.0)
    historical_yield_kg = models.FloatField(blank=True, null=True)
    ai_recommendation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        farm_name = self.farm.name if self.farm else "No farm"
        return f"{self.name} ({farm_name})"