
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status
from .models import Alert, Farm, Livestock, MarketPrice, Settings
from .serializers import (
    AlertSerializer,
    FarmCreateSerializer,
    FarmOutSerializer,
    FarmOverviewSerializer,
    LivestockSerializer,
    MarketPriceSerializer,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_farms(request):
    farms = Farm.objects.all()
    serializer = FarmOutSerializer(farms, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_farm(request):
    serializer = FarmCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    farm = serializer.save(owner=request.user)
    Settings.objects.create(farm=farm)  # default settings row
    out = FarmOutSerializer(farm)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_owned_farms(request):
    farms = Farm.objects.filter(owner=request.user).order_by('name').values('id', 'name')
    return Response(list(farms))


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_farm(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
    serializer = FarmCreateSerializer(
        farm,
        data=request.data,
        partial=request.method == 'PATCH',
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    farm = serializer.save()
    return Response(FarmOutSerializer(farm).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_farm(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
    farm.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_farm(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id)
    serializer = FarmOutSerializer(farm)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_farm_overview(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)

    active_crops = farm.registered_crops.count()
    total_crop_yield_kg = farm.registered_crops.aggregate(
        total=Sum('historical_yield_kg')
    )['total'] or 0
    open_pest_alerts = farm.pest_alerts.filter(resolved=False).count()
    livestock_count = farm.livestock.count()
    latest_soil = farm.soil_readings.order_by('-recorded_at').first()
    latest_weather = farm.weather_logs.order_by('-recorded_at').first()
    upcoming_irrigation = farm.irrigation_events.filter(status='scheduled').order_by('scheduled_at')[:5]
    recent_alerts = farm.alerts.order_by('-created_at')[:8]

    overview_data = {
        'farm': farm,
        'active_crops': active_crops,
        'total_crop_yield_kg': total_crop_yield_kg,
        'open_pest_alerts': open_pest_alerts,
        'livestock_count': livestock_count,
        'latest_soil': latest_soil,
        'latest_weather': latest_weather,
        'upcoming_irrigation': upcoming_irrigation,
        'recent_alerts': recent_alerts,
    }
    serializer = FarmOverviewSerializer(overview_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_livestock(request):
    farm = get_object_or_404(Farm, pk=request.query_params.get('farm_id'), owner=request.user)
    return Response(LivestockSerializer(farm.livestock.all(), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_market_prices(request):
    return Response(MarketPriceSerializer(MarketPrice.objects.all(), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_alerts(request):
    farm = get_object_or_404(Farm, pk=request.query_params.get('farm_id'), owner=request.user)
    return Response(AlertSerializer(farm.alerts.all().order_by('-created_at'), many=True).data)
