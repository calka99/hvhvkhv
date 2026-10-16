from datetime import timedelta

from django.utils import timezone

from .models import Alert, Farm


ALERT_DEDUPE_WINDOW = timedelta(hours=24)


def _create_alert_once(farm, category, severity, message):
    cutoff = timezone.now() - ALERT_DEDUPE_WINDOW
    exists = Alert.objects.filter(
        farm=farm,
        category=category,
        message=message,
        created_at__gte=cutoff,
    ).exists()
    if not exists:
        Alert.objects.create(
            farm=farm,
            category=category,
            severity=severity,
            message=message,
        )


def refresh_farm_alerts(farm):
    latest_soil = farm.soil_readings.order_by('-recorded_at').first()
    if latest_soil:
        if latest_soil.moisture_pct < 20:
            _create_alert_once(
                farm,
                'soil moisture',
                'critical',
                f'Soil moisture is critically low at {latest_soil.moisture_pct:.0f}%.',
            )
        elif latest_soil.moisture_pct < 30:
            _create_alert_once(
                farm,
                'soil moisture',
                'warning',
                f'Soil moisture is low at {latest_soil.moisture_pct:.0f}%.',
            )

        if latest_soil.degradation_risk in {'high', 'critical'}:
            _create_alert_once(
                farm,
                'soil health',
                latest_soil.degradation_risk,
                f'Soil degradation risk is {latest_soil.degradation_risk}.',
            )

    latest_weather = farm.weather_logs.order_by('-recorded_at').first()
    if latest_weather and latest_weather.rainfall_mm > 12:
        _create_alert_once(
            farm,
            'weather',
            'warning',
            f'Heavy rainfall recorded at {latest_weather.rainfall_mm:.1f} mm.',
        )

    overdue_irrigation_zone = farm.irrigation_events.filter(
        status='scheduled',
        scheduled_at__lt=timezone.now(),
    ).values_list('zone', flat=True).first()
    if overdue_irrigation_zone:
        _create_alert_once(
            farm,
            'irrigation',
            'warning',
            f'Irrigation for {overdue_irrigation_zone} is overdue.',
        )

    high_risk_pest = farm.pest_alerts.filter(
        resolved=False,
        risk_level__in=['high', 'critical'],
    ).first()
    if high_risk_pest:
        _create_alert_once(
            farm,
            'pest risk',
            'critical',
            f'{high_risk_pest.pest_or_disease} detected on {high_risk_pest.crop_name}.',
        )


def refresh_user_farm_alerts(user):
    for farm in Farm.objects.filter(owner=user):
        refresh_farm_alerts(farm)
