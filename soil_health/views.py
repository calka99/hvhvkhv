from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from farm_overview.models import Farm, SoilReading
from .serializers import SoilReadingSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def soil_readings(request):
	farm_id = request.query_params.get('farm_id') or request.data.get('farm_id')
	if not farm_id:
		return Response({'detail': 'farm_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

	farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)

	if request.method == 'GET':
		readings = SoilReading.objects.filter(farm=farm).order_by('recorded_at')
		return Response(SoilReadingSerializer(readings, many=True).data)

	serializer = SoilReadingSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	reading = serializer.save(farm=farm)
	return Response(SoilReadingSerializer(reading).data, status=status.HTTP_201_CREATED)
