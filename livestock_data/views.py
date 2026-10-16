from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from farm_overview.models import Farm, Livestock, LivestockHealthAlert
from .models import LivestockType
from .serializers import LivestockSerializer, LivestockHealthAlertSerializer, LivestockTypeSerializer


@api_view(['GET'])
def livestock_types(request):
	return Response(LivestockTypeSerializer(LivestockType.objects.all(), many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def livestock_records(request):
	farm_id = request.query_params.get('farm_id') or request.data.get('farm_id')
	if request.method == 'POST' and not farm_id:
		return Response({'detail': 'farm_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

	if farm_id:
		farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
		if request.method == 'POST' and farm.farm_type.strip().lower() not in {'livestock', 'mixed', 'aquaculture'}:
			return Response(
				{'detail': 'Livestock can only be added to livestock, mixed, or aquaculture farms. Create a suitable farm first.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

	if request.method == 'GET':
		records = Livestock.objects.filter(farm__owner=request.user)
		if farm_id:
			records = records.filter(farm=farm)
		records = records.select_related('farm').order_by('species', 'id')
		return Response(LivestockSerializer(records, many=True).data)

	serializer = LivestockSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	record = serializer.save(farm=farm)
	return Response(LivestockSerializer(record).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def livestock_record_detail(request, livestock_id):
	record = get_object_or_404(Livestock, pk=livestock_id, farm__owner=request.user)
	update_data = request.data.copy()
	farm_id = update_data.pop('farm_id', None)
	farm = record.farm

	if farm_id:
		farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
		if farm.farm_type.strip().lower() not in {'livestock', 'mixed', 'aquaculture'}:
			return Response(
				{'detail': 'Livestock can only be assigned to livestock, mixed, or aquaculture farms.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

	serializer = LivestockSerializer(record, data=update_data, partial=True)
	serializer.is_valid(raise_exception=True)
	updated_record = serializer.save(farm=farm)
	return Response(LivestockSerializer(updated_record).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def livestock_health_alerts(request):
	farm_id = request.query_params.get('farm_id') or request.data.get('farm_id')
	if request.method == 'POST' and not farm_id:
		return Response({'detail': 'farm_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

	if farm_id:
		farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)

	if request.method == 'GET':
		alerts = LivestockHealthAlert.objects.filter(farm__owner=request.user)
		if farm_id:
			alerts = alerts.filter(farm=farm)
		alerts = alerts.select_related('farm', 'livestock').order_by('-detected_at')
		return Response(LivestockHealthAlertSerializer(alerts, many=True).data)

	livestock_id = request.data.get('livestock_id')
	if not livestock_id:
		return Response({'detail': 'livestock_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

	livestock = get_object_or_404(Livestock, pk=livestock_id, farm=farm)
	serializer = LivestockHealthAlertSerializer(data={
		'farm': farm.id,
		'livestock': livestock.id,
		'disease_name': request.data.get('disease_name'),
		'severity': request.data.get('severity', 'medium'),
		'recommended_action': request.data.get('recommended_action', ''),
	})
	serializer.is_valid(raise_exception=True)
	alert = serializer.save(farm=farm, livestock=livestock)
	return Response(LivestockHealthAlertSerializer(alert).data, status=status.HTTP_201_CREATED)
