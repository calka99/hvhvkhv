from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from .models import Category, Crop
from .serializers import CategorySerializer, CropSerializer


# Category Views

@api_view(['GET'])
def list_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


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
def list_crops(request):
    farm_id = request.query_params.get('farm_id')
    crops = Crop.objects.select_related('category').all()
    if farm_id:
        crops = crops.filter(farm_id=farm_id)
    serializer = CropSerializer(crops, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_crop(request):
    serializer = CropSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    crop = serializer.save()
    out = CropSerializer(crop)
    return Response(out.data, status=status.HTTP_201_CREATED)


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
@permission_classes([IsAdminUser])
def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id)
    crop.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
