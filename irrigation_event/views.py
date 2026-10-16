from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from farm_overview.models import Farm, IrrigationEvent
from .serializers import IrrigationEventSerializer


# Irrigation Views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_irrigation(request):
    farm_id = request.query_params.get('farm_id')
    irrigation = IrrigationEvent.objects.filter(farm__owner=request.user)
    if farm_id:
        irrigation = irrigation.filter(farm_id=farm_id, farm__owner=request.user)
    irrigation = irrigation.order_by('scheduled_at')
    records = IrrigationEventSerializer(irrigation, many=True).data
    now = timezone.now()
    for record, event in zip(records, irrigation):
        if event.status == 'scheduled' and event.scheduled_at <= now:
            record['status'] = 'critical'
    return Response(records)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_irrigation(request):
    farm = get_object_or_404(Farm, pk=request.data.get('farm_id'), owner=request.user)
    payload = request.data.copy()
    payload.pop('farm_id', None)
    serializer = IrrigationEventSerializer(data=payload)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    irrigation = serializer.save(farm=farm)
    out = IrrigationEventSerializer(irrigation)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_irrigation(request, irrigation_id):
    irrigation = get_object_or_404(IrrigationEvent, pk=irrigation_id)
    serializer = IrrigationEventSerializer(irrigation)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_irrigation(request, irrigation_id):
    irrigation = get_object_or_404(IrrigationEvent, pk=irrigation_id)
    serializer = IrrigationEventSerializer(irrigation, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_irrigation(request, irrigation_id):
    irrigation = get_object_or_404(IrrigationEvent, pk=irrigation_id)
    irrigation.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_irrigation_status(request, irrigation_id):
    irrigation = get_object_or_404(IrrigationEvent, pk=irrigation_id, farm__owner=request.user)
    new_status = request.query_params.get('status')
    if not new_status:
        return Response({'error': 'status parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = IrrigationEventSerializer(irrigation, data={'status': new_status}, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)
