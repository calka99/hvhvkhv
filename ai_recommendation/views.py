import logging

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from farm_overview.models import Farm
from reports.views import build_activity_data, parse_month
from settings.models import FarmPreference

from .models import Recommendation
from .services import generate_ai_recommendations

logger = logging.getLogger(__name__)


def _month_from_request(request, method):
	value = request.data.get('month') if method == 'POST' else request.query_params.get('month')
	if not value:
		return timezone.localdate().replace(day=1)
	try:
		return parse_month(value)
	except ValueError as error:
		raise ValueError('month must use YYYY-MM format.') from error


def _monthly_activity(farm, month):
	activity_data = build_activity_data(farm, month)
	activity_counts = activity_data['activity_counts']
	has_activity = any(
		count > 0
		for key, count in activity_counts.items()
		if key != 'analytics_snapshots'
	)
	recommendation_data = {
		**activity_data,
		'activity_counts': {
			key: count for key, count in activity_counts.items()
			if key != 'analytics_snapshots'
		},
		'activities': {
			key: records for key, records in activity_data['activities'].items()
			if key not in {'livestock_snapshot', 'analytics_snapshots'}
		},
	}
	return has_activity, recommendation_data['activity_counts'], recommendation_data


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommendations(request):
	try:
		month = _month_from_request(request, request.method)
	except ValueError as error:
		return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

	farm_id = request.data.get('farm_id')
	if not farm_id:
		return Response(
			{'detail': 'Select a farm to generate recommendations.'},
			status=status.HTTP_400_BAD_REQUEST,
		)
	farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
	preference, _ = FarmPreference.objects.get_or_create(owner=request.user)
	if not preference.ai_recommendations_enabled:
		return Response(
			{'detail': 'AI recommendations are disabled in your account settings.'},
			status=status.HTTP_403_FORBIDDEN,
		)

	has_activity, _, activity_data = _monthly_activity(farm, month)
	if not has_activity:
		return Response({
			'farm_id': farm.id,
			'farm_name': farm.name,
			'month': month.isoformat(),
			'status': 'no_activity',
			'recommendation_count': 0,
			'detail': 'No farm activities were recorded for this month, so no recommendations were generated.',
		})

	if not settings.GROQ_API_KEY:
		return Response(
			{'detail': 'AI recommendations are not configured. Set GROQ_API_KEY in the backend environment and restart Django.'},
			status=status.HTTP_503_SERVICE_UNAVAILABLE,
		)

	try:
		activity_data['activities'].pop('livestock_snapshot', None)
		recommendation_data = generate_ai_recommendations(farm, month, activity_data)
	except Exception:
		logger.exception(
			'Monthly AI recommendation generation failed for farm_id=%s, user_id=%s.',
			farm.id,
			request.user.id,
		)
		return Response(
			{'detail': 'AI recommendation generation failed. Existing recommendations were not changed; check the backend logs for the provider error.'},
			status=status.HTTP_503_SERVICE_UNAVAILABLE,
		)

	Recommendation.objects.filter(
		farm=farm,
		month=month,
		is_active=True,
		source_data__generator='ai',
	).update(is_active=False)
	records = Recommendation.objects.bulk_create([
		Recommendation(
			farm=farm,
			month=month,
			**{**item, 'source_data': {'generator': 'ai'}},
		)
		for item in recommendation_data
	])
	return Response({
		'farm_id': farm.id,
		'farm_name': farm.name,
		'month': month.isoformat(),
		'status': 'generated' if records else 'no_recommendations',
		'recommendation_count': len(records),
		'detail': (
			f'Generated {len(records)} recommendation(s) for {farm.name}.'
			if records else
			'The recorded activity does not support a specific recommendation.'
		),
	}, status=status.HTTP_201_CREATED)
