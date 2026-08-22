from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from farm_overview.models import Farm, Livestock
from .serializers import LivestockSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def livestock_records(request):
	farm_id = request.query_params.get('farm_id') or request.data.get('farm_id')
	if not farm_id:
		return Response({'detail': 'farm_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

	farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)

	if request.method == 'GET':
		records = Livestock.objects.filter(farm=farm).order_by('species', 'id')
		return Response(LivestockSerializer(records, many=True).data)

	serializer = LivestockSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	record = serializer.save(farm=farm)
	return Response(LivestockSerializer(record).data, status=status.HTTP_201_CREATED)
