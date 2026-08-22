from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from farm_overview.models import Farm, Settings
from .serializers import SettingsSerializer, SettingsUpdateSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_settings(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id,owner=request.user)
    settings_obj = Settings.objects.filter(farm=farm).first()
    if not settings_obj:
        settings_obj = Settings.objects.create(farm=farm)
    serializer = SettingsSerializer(settings_obj)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_settings(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
    settings_obj = Settings.objects.filter(farm=farm).first()
    if not settings_obj:
        settings_obj = Settings.objects.create(farm=farm)

    serializer = SettingsUpdateSerializer(settings_obj, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(SettingsSerializer(settings_obj).data)
