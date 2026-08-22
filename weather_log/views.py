import json
from datetime import datetime, timedelta
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from farm_overview.models import Farm, WeatherLog
from .serializers import WeatherLogSerializer


def _fetch_json(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _build_weather_summary(temperature_c, humidity_pct, rainfall_mm, wind_kph):
    if rainfall_mm > 12:
        summary = "Heavy rain and cloudy skies are expected."
        action = "Reduce irrigation and monitor drainage conditions."
    elif rainfall_mm > 2:
        summary = "Light rainfall is expected throughout the day."
        action = "Delay irrigation and check runoff risk."
    elif temperature_c > 30:
        summary = "Warm and dry conditions are forecasted."
        action = "Increase irrigation monitoring for heat stress."
    elif humidity_pct < 40:
        summary = "Conditions are dry and relatively low in humidity."
        action = "Watch crop water demand and soil moisture closely."
    elif temperature_c < 18:
        summary = "Cool conditions are expected today."
        action = "Planting and field operations can proceed with normal monitoring."
    else:
        summary = "Conditions are moderate and suitable for routine field work."
        action = "Continue normal field monitoring and irrigation planning."

    return summary, action


def _build_live_weather_records(farm):
    location = (farm.location or "").strip()
    if not location:
        raise ValueError("Farm location is missing.")

    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(location)}&count=1&language=en&format=json"
    )
    geo_data = _fetch_json(geo_url)
    results = geo_data.get("results") or []
    if not results:
        raise ValueError(f"Unable to find coordinates for farm location: {location}")

    place = results[0]
    latitude = place["latitude"]
    longitude = place["longitude"]

    forecast_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
        "&timezone=auto&forecast_days=7"
    )
    forecast_data = _fetch_json(forecast_url)
    daily = forecast_data.get("daily") or {}
    times = daily.get("time") or []
    max_temps = daily.get("temperature_2m_max") or [0 for _ in times]
    min_temps = daily.get("temperature_2m_min") or [0 for _ in times]
    rainfalls = daily.get("precipitation_sum") or [0 for _ in times]
    winds = daily.get("wind_speed_10m_max") or [0 for _ in times]

    current = forecast_data.get("current") or {}
    latest_temp = current.get("temperature_2m")
    latest_humidity = current.get("relative_humidity_2m")
    latest_rain = current.get("precipitation")
    latest_wind = current.get("wind_speed_10m")

    records = []
    for index, day in enumerate(times):
        max_temp = max_temps[index] if index < len(max_temps) else 0
        min_temp = min_temps[index] if index < len(min_temps) else 0
        avg_temp = ((max_temp or 0) + (min_temp or 0)) / 2
        rainfall = rainfalls[index] if index < len(rainfalls) else 0
        wind = winds[index] if index < len(winds) else 0

        if index == len(times) - 1:
            temperature_c = latest_temp if latest_temp is not None else avg_temp
            humidity_pct = latest_humidity if latest_humidity is not None else 60
            rainfall_mm = latest_rain if latest_rain is not None else rainfall
            wind_kph = latest_wind if latest_wind is not None else wind
        else:
            temperature_c = avg_temp
            humidity_pct = 60
            rainfall_mm = rainfall
            wind_kph = wind

        summary, action = _build_weather_summary(temperature_c, humidity_pct, rainfall_mm, wind_kph)
        records.append({
            "id": index + 1,
            "farm_id": farm.id,
            "recorded_at": f"{day}T12:00:00Z",
            "temperature_c": float(temperature_c),
            "humidity_pct": float(humidity_pct),
            "rainfall_mm": float(rainfall_mm),
            "wind_kph": float(wind_kph),
            "forecast_summary": summary,
            "recommended_action": action,
        })

    return records


# Weather Views

@api_view(['GET'])
def list_weather(request):
    farm_id = request.query_params.get('farm')

    if farm_id:
        farm = get_object_or_404(Farm, pk=farm_id)
        try:
            live_records = _build_live_weather_records(farm)
            return Response(live_records)
        except Exception:
            weather = WeatherLog.objects.filter(farm=farm).order_by('recorded_at')
            serializer = WeatherLogSerializer(weather, many=True)
            return Response(serializer.data)

    weather = WeatherLog.objects.all().order_by('recorded_at')
    serializer = WeatherLogSerializer(weather, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_weather(request):
    serializer = WeatherLogSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    weather = serializer.save()
    out = WeatherLogSerializer(weather)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_weather(request, weather_id):
    weather = get_object_or_404(WeatherLog, pk=weather_id)
    serializer = WeatherLogSerializer(weather)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_weather(request, weather_id):
    weather = get_object_or_404(WeatherLog, pk=weather_id)
    serializer = WeatherLogSerializer(weather, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_weather(request, weather_id):
    weather = get_object_or_404(WeatherLog, pk=weather_id)
    weather.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
