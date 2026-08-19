
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from .models import Farm, Settings
from .serializers import (
    FarmCreateSerializer,
    FarmOutSerializer,
    FarmOverviewSerializer,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

# Create your views here.

@api_view(['GET'])
def list_farms(request):
    farms = Farm.objects.all()
    serializer = FarmOutSerializer(farms, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_farm(request):
    serializer = FarmCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    farm = serializer.save()
    Settings.objects.create(farm=farm)  # default settings row
    out = FarmOutSerializer(farm)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_farm(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id)
    serializer = FarmOutSerializer(farm)
    return Response(serializer.data)


@api_view(['GET'])
def get_farm_overview(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id)

    active_crops = farm.crops.count()
    open_pest_alerts = farm.pest_alerts.filter(resolved=False).count()
    livestock_count = farm.livestock.count()
    latest_soil = farm.soil_readings.order_by('-recorded_at').first()
    latest_weather = farm.weather_logs.order_by('-recorded_at').first()
    upcoming_irrigation = farm.irrigation_events.filter(status='scheduled').order_by('scheduled_at')[:5]
    recent_alerts = farm.alerts.order_by('-created_at')[:8]

    overview_data = {
        'farm': farm,
        'active_crops': active_crops,
        'open_pest_alerts': open_pest_alerts,
        'livestock_count': livestock_count,
        'latest_soil': latest_soil,
        'latest_weather': latest_weather,
        'upcoming_irrigation': upcoming_irrigation,
        'recent_alerts': recent_alerts,
    }
    serializer = FarmOverviewSerializer(overview_data)
    return Response(serializer.data)
