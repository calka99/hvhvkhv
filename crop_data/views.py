from datetime import timedelta

from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from farm_overview.models import Farm
from rest_framework.decorators import api_view, permission_classes

from .models import Category, Crop, CropType
from .serializers import (
    CategorySerializer,
    CropHarvestSerializer,
    CropSerializer,
    CropTypeSerializer,
)


# Category Views

@api_view(['GET'])
def list_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_crop_types(request):
    crop_types = CropType.objects.select_related('category').exclude(name=F('category__name'))
    return Response(CropTypeSerializer(crop_types, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    category = serializer.save()
    out = CategorySerializer(category)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    serializer = CategorySerializer(category)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    serializer = CategorySerializer(category, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# Crop Views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_crops(request):
    farm_id = request.query_params.get('farm_id')
    crops = Crop.objects.select_related('category', 'farm').filter(farm__owner=request.user)
    if farm_id:
        crops = crops.filter(farm_id=farm_id, farm__owner=request.user)
    serializer = CropSerializer(crops, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_crop(request):
    farm = get_object_or_404(Farm, pk=request.data.get('farm_id'), owner=request.user)
    crop_type = get_object_or_404(CropType, pk=request.data.get('crop_type_id'))
    payload = request.data.copy()
    payload.pop('farm_id', None)
    payload.pop('crop_type_id', None)
    payload.pop('expected_harvest_date', None)
    payload['category'] = crop_type.category_id
    payload['name'] = crop_type.name
    serializer = CropSerializer(data=payload)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    crop = serializer.save(
        farm=farm,
        crop_type=crop_type,
        expected_harvest_date=serializer.validated_data['planting_date'] + timedelta(days=crop_type.lifespan_days),
    )
    out = CropSerializer(crop)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_crop_harvested(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id, farm__owner=request.user)
    serializer = CropHarvestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if crop.expected_harvest_date is None or timezone.now() < crop.expected_harvest_date:
        raise ValidationError({'detail': 'This crop cannot be harvested before its expected harvest date.'})

    if crop.harvested_at is None:
        crop.historical_yield_kg = serializer.validated_data['historical_yield_kg']
        crop.growth_stage = 'harvested'
        crop.harvested_at = timezone.now()
        crop.save(update_fields=['historical_yield_kg', 'growth_stage', 'harvested_at', 'updated_at'])
    return Response(CropSerializer(crop).data)


@api_view(['GET'])
def get_crop(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id)
    serializer = CropSerializer(crop)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_crop(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id)
    serializer = CropSerializer(crop, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id, farm__owner=request.user)
    crop.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
