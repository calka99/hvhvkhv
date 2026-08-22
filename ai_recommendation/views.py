from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from farm_overview.models import Farm
from .models import Recommendation
from .serializers import RecommendationSerializer


def build_recommendations(farm):
	recommendations = []
	soil = farm.soil_readings.order_by('-recorded_at').first()
	weather = farm.weather_logs.order_by('-recorded_at').first()
	open_pests = farm.pest_alerts.filter(resolved=False).count()

	if soil and soil.moisture_pct < 30:
		recommendations.append({
			'category': 'irrigation',
			'title': 'Increase irrigation attention',
			'message': f'Soil moisture is {soil.moisture_pct:.1f}%. Check irrigation for dry zones.',
			'priority': 'high',
			'source_data': {'moisture_pct': soil.moisture_pct},
		})
	elif soil and soil.moisture_pct > 80:
		recommendations.append({
			'category': 'irrigation',
			'title': 'Reduce irrigation',
			'message': f'Soil moisture is {soil.moisture_pct:.1f}%. Pause unnecessary watering and check drainage.',
			'priority': 'medium',
			'source_data': {'moisture_pct': soil.moisture_pct},
		})

	if soil and not 5.5 <= soil.ph_level <= 7.5:
		recommendations.append({
			'category': 'soil',
			'title': 'Review soil pH',
			'message': f'Soil pH is {soil.ph_level:.1f}. Test the affected area before applying amendments.',
			'priority': 'medium',
			'source_data': {'ph_level': soil.ph_level},
		})

	if weather and weather.rainfall_mm > 20:
		recommendations.append({
			'category': 'weather',
			'title': 'Inspect fields after heavy rain',
			'message': f'{weather.rainfall_mm:.1f} mm of rain was recorded. Check drainage and root exposure.',
			'priority': 'medium',
			'source_data': {'rainfall_mm': weather.rainfall_mm},
		})

	if open_pests:
		recommendations.append({
			'category': 'pest',
			'title': 'Review open pest alerts',
			'message': f'{open_pests} unresolved pest alert(s) need attention.',
			'priority': 'high',
			'source_data': {'open_pest_alerts': open_pests},
		})

	if not recommendations:
		recommendations.append({
			'category': 'general',
			'title': 'Maintain current farm plan',
			'message': 'Current readings show no immediate issues. Continue monitoring soil, weather, and crops.',
			'priority': 'low',
			'source_data': {},
		})

	return recommendations


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def recommendations(request):
	farm = get_object_or_404(Farm, pk=request.query_params.get('farm_id'), owner=request.user)

	if request.method == 'POST':
		Recommendation.objects.filter(farm=farm, is_active=True).update(is_active=False)
		records = Recommendation.objects.bulk_create([
			Recommendation(farm=farm, **item) for item in build_recommendations(farm)
		])
		return Response(RecommendationSerializer(records, many=True).data, status=status.HTTP_201_CREATED)

	records = Recommendation.objects.filter(farm=farm, is_active=True)
	if not records.exists():
		records = [Recommendation(farm=farm, **item) for item in build_recommendations(farm)]
	return Response(RecommendationSerializer(records, many=True).data)
