from datetime import datetime, time

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from farm_overview.models import (
	Alert,
	AnalyticsSnapshot,
	Crop,
	Farm,
	IrrigationEvent,
	Livestock,
	PestAlert,
	SoilReading,
	WeatherLog,
)

from .models import MonthlyFarmReport
from .serializers import MonthlyFarmReportSerializer


def parse_month(value):
	try:
		return datetime.strptime(value, '%Y-%m').date().replace(day=1)
	except (TypeError, ValueError):
		raise ValueError('month must use YYYY-MM format.')


def month_bounds(month):
	next_month = month.replace(
		year=month.year + (month.month == 12),
		month=1 if month.month == 12 else month.month + 1,
	)
	start = timezone.make_aware(datetime.combine(month, time.min))
	end = timezone.make_aware(datetime.combine(next_month, time.min))
	return start, end


def iso(value):
	return value.isoformat() if value else None


def build_activity_data(farm, month):
	start, end = month_bounds(month)
	crops = Crop.objects.filter(farm=farm, planting_date__gte=start, planting_date__lt=end)
	soil_readings = SoilReading.objects.filter(farm=farm, recorded_at__gte=start, recorded_at__lt=end)
	weather_logs = WeatherLog.objects.filter(farm=farm, recorded_at__gte=start, recorded_at__lt=end)
	irrigation_events = IrrigationEvent.objects.filter(farm=farm, scheduled_at__gte=start, scheduled_at__lt=end)
	pest_alerts = PestAlert.objects.filter(farm=farm, detected_at__gte=start, detected_at__lt=end)
	alerts = Alert.objects.filter(farm=farm, created_at__gte=start, created_at__lt=end)
	analytics = AnalyticsSnapshot.objects.filter(farm=farm, period_label=month.strftime('%Y-%m'))
	livestock = Livestock.objects.filter(farm=farm)

	soil_values = list(soil_readings.values('moisture_pct', 'ph_level'))
	average = lambda key: round(sum(item[key] for item in soil_values) / len(soil_values), 2) if soil_values else None
	rainfall = sum(log.rainfall_mm for log in weather_logs)
	water = sum(event.water_liters or 0 for event in irrigation_events)
	feedback_signals = []
	unresolved_pests = pest_alerts.filter(resolved=False).count()
	high_risk_pests = pest_alerts.filter(risk_level__in=['high', 'critical']).count()

	if unresolved_pests:
		feedback_signals.append(f'{unresolved_pests} pest alert(s) remain unresolved.')
	if high_risk_pests:
		feedback_signals.append(f'{high_risk_pests} high-risk pest alert(s) need urgent review.')
	if irrigation_events.exists() and water == 0:
		feedback_signals.append('Irrigation events have no recorded water volume.')
	if average('moisture_pct') is not None and average('moisture_pct') < 30:
		feedback_signals.append('Average soil moisture is below 30%; review irrigation planning.')
	if rainfall == 0 and not irrigation_events.exists():
		feedback_signals.append('No rainfall or irrigation was recorded; check water availability.')

	return {
		'period': {'month': month.strftime('%Y-%m'), 'start': month.isoformat(), 'end': end.date().isoformat()},
		'activity_counts': {
			'crop_plantings': crops.count(),
			'soil_readings': soil_readings.count(),
			'weather_logs': weather_logs.count(),
			'irrigation_events': irrigation_events.count(),
			'pest_alerts': pest_alerts.count(),
			'farm_alerts': alerts.count(),
			'analytics_snapshots': analytics.count(),
		},
		'measurements': {
			'rainfall_mm': round(rainfall, 2),
			'irrigation_water_liters': round(water, 2),
			'irrigation_minutes': sum(event.duration_minutes for event in irrigation_events),
			'average_soil_moisture_pct': average('moisture_pct'),
			'average_soil_ph': average('ph_level'),
		},
		'activities': {
			'crop_plantings': [
				{'id': crop.id, 'name': crop.name, 'variety': crop.variety, 'planted_at': iso(crop.planting_date)}
				for crop in crops
			],
			'soil_readings': [
				{'id': item.id, 'recorded_at': iso(item.recorded_at), 'moisture_pct': item.moisture_pct, 'ph_level': item.ph_level, 'degradation_risk': item.degradation_risk}
				for item in soil_readings
			],
			'weather_logs': [
				{'id': item.id, 'recorded_at': iso(item.recorded_at), 'temperature_c': item.temperature_c, 'humidity_pct': item.humidity_pct, 'rainfall_mm': item.rainfall_mm, 'recommended_action': item.recommended_action}
				for item in weather_logs
			],
			'irrigation_events': [
				{'id': item.id, 'zone': item.zone, 'scheduled_at': iso(item.scheduled_at), 'duration_minutes': item.duration_minutes, 'water_liters': item.water_liters, 'status': item.status}
				for item in irrigation_events
			],
			'pest_alerts': [
				{'id': item.id, 'crop_name': item.crop_name, 'pest_or_disease': item.pest_or_disease, 'risk_level': item.risk_level, 'detected_at': iso(item.detected_at), 'resolved': item.resolved, 'recommended_action': item.recommended_action}
				for item in pest_alerts
			],
			'farm_alerts': [
				{'id': item.id, 'category': item.category, 'severity': item.severity, 'message': item.message, 'created_at': iso(item.created_at), 'acknowledged': item.acknowledged}
				for item in alerts
			],
			'livestock_snapshot': [
				{'id': item.id, 'species': item.species, 'count': item.count, 'health_status': item.health_status, 'productivity_metric': item.productivity_metric}
				for item in livestock
			],
			'analytics_snapshots': list(analytics.values()),
		},
		'feedback_signals': feedback_signals,
	}


def generate_report(farm, month, user):
	report, _ = MonthlyFarmReport.objects.get_or_create(farm=farm, month=month)
	report.activity_data = build_activity_data(farm, month)
	report.generated_by = user
	report.generated_at = timezone.now()
	report.save(update_fields=['activity_data', 'generated_by', 'generated_at'])
	return report


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_monthly_reports(request):
	month_value = request.query_params.get('month')
	if month_value:
		try:
			month = parse_month(month_value)
		except ValueError as error:
			return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
		reports = MonthlyFarmReport.objects.filter(month=month)
	else:
		reports = MonthlyFarmReport.objects.all()
	farm_id = request.query_params.get('farm_id')
	if farm_id:
		reports = reports.filter(farm_id=farm_id)
	return Response(MonthlyFarmReportSerializer(reports, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def generate_monthly_reports(request):
	try:
		month = parse_month(request.data.get('month'))
	except ValueError as error:
		return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
	farms = Farm.objects.filter(pk=request.data.get('farm_id')) if request.data.get('farm_id') else Farm.objects.all()
	reports = [generate_report(farm, month, request.user) for farm in farms]
	return Response(MonthlyFarmReportSerializer(reports, many=True).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_monthly_report(request, report_id):
	report = get_object_or_404(MonthlyFarmReport, pk=report_id)
	serializer = MonthlyFarmReportSerializer(report, data=request.data, partial=True)
	serializer.is_valid(raise_exception=True)
	serializer.save()
	return Response(serializer.data)
