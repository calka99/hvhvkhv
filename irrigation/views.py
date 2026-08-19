from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from farm_overview.models import IrrigationEvent
from .serializers import IrrigationEventSerializer


# Irrigation Views

@api_view(['GET'])
def list_irrigation(request):
    farm_id = request.query_params.get('farm_id')
    irrigation = IrrigationEvent.objects.all()
    if farm_id:
        irrigation = irrigation.filter(farm_id=farm_id)
    irrigation = irrigation.order_by('scheduled_at')
    serializer = IrrigationEventSerializer(irrigation, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_irrigation(request):
    serializer = IrrigationEventSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    irrigation = serializer.save()
    out = IrrigationEventSerializer(irrigation)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_irrigation(request, irrigation_id):
    irrigation = get_object_or_404(IrrigationEvent, pk=irrigation_id)
    serializer = IrrigationEventSerializer(irrigation)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
def update_irrigation_status(request, irrigation_id):
    irrigation = get_object_or_404(IrrigationEvent, pk=irrigation_id)
    new_status = request.query_params.get('status')
    if not new_status:
        return Response({'error': 'status parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    irrigation.status = new_status
    irrigation.save()
    serializer = IrrigationEventSerializer(irrigation)
    return Response(serializer.data)
