from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from farm_overview.models import Farm, PestAlert
from .serializers import PestAlertSerializer


# Pest Alert Views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pest_alerts(request):
    farm_id = request.query_params.get('farm_id')
    pests = PestAlert.objects.filter(farm__owner=request.user)
    if farm_id:
        pests = pests.filter(farm_id=farm_id, farm__owner=request.user)
    pests = pests.order_by('-detected_at')
    serializer = PestAlertSerializer(pests, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_pest_alert(request):
    farm = get_object_or_404(Farm, pk=request.data.get('farm_id'), owner=request.user)
    payload = request.data.copy()
    payload.pop('farm_id', None)
    serializer = PestAlertSerializer(data=payload)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    pest = serializer.save(farm=farm)
    out = PestAlertSerializer(pest)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_pest_alert(request, pest_alert_id):
    pest = get_object_or_404(PestAlert, pk=pest_alert_id)
    serializer = PestAlertSerializer(pest)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_pest_alert(request, pest_alert_id):
    pest = get_object_or_404(PestAlert, pk=pest_alert_id)
    serializer = PestAlertSerializer(pest, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_pest_alert(request, pest_alert_id):
    pest = get_object_or_404(PestAlert, pk=pest_alert_id)
    pest.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def resolve_pest_alert(request, pest_alert_id):
    pest = get_object_or_404(PestAlert, pk=pest_alert_id, farm__owner=request.user)
    pest.resolved = True
    pest.save()
    serializer = PestAlertSerializer(pest)
    return Response(serializer.data)




