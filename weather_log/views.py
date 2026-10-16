# import json
# from datetime import datetime, timedelta
# from urllib.parse import quote
# from urllib.request import Request, urlopen

# from django.shortcuts import get_object_or_404
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAdminUser, IsAuthenticated
# from rest_framework.decorators import api_view, permission_classes

# from farm_overview.models import Farm, WeatherLog
# from .serializers import WeatherLogSerializer


# def _fetch_json(url):
#     request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
#     with urlopen(request, timeout=20) as response:
#         return json.loads(response.read().decode("utf-8"))


# def _geocode_location(location):
#     geo_url = (
#         "https://geocoding-api.open-meteo.com/v1/search"
#         f"?name={quote(location)}&count=1&language=en&format=json"
#     )
#     geo_data = _fetch_json(geo_url)
#     results = geo_data.get("results") or []
#     if not results:
#         raise ValueError(f"Unable to find coordinates for farm location: {location}")
#     return results[0]


# def _build_weather_summary(temperature_c, humidity_pct, rainfall_mm, wind_kph):
#     if rainfall_mm > 12:
#         summary = "Heavy rain and cloudy skies are expected."
#         action = "Reduce irrigation and monitor drainage conditions."
#     elif rainfall_mm > 2:
#         summary = "Light rainfall is expected throughout the day."
#         action = "Delay irrigation and check runoff risk."
#     elif temperature_c > 30:
#         summary = "Warm and dry conditions are forecasted."
#         action = "Increase irrigation monitoring for heat stress."
#     elif humidity_pct < 40:
#         summary = "Conditions are dry and relatively low in humidity."
#         action = "Watch crop water demand and soil moisture closely."
#     elif temperature_c < 18:
#         summary = "Cool conditions are expected today."
#         action = "Planting and field operations can proceed with normal monitoring."
#     else:
#         summary = "Conditions are moderate and suitable for routine field work."
#         action = "Continue normal field monitoring and irrigation planning."

#     return summary, action


# def _build_live_weather_records(farm):
#     location = (farm.location or "").strip()
#     if not location:
#         raise ValueError("Farm location is missing.")

#     place = _geocode_location(location)
#     latitude = place["latitude"]
#     longitude = place["longitude"]

#     forecast_url = (
#         "https://api.open-meteo.com/v1/forecast"
#         f"?latitude={latitude}&longitude={longitude}"
#         "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
#         "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
#         "&timezone=auto&forecast_days=7"
#     )
#     forecast_data = _fetch_json(forecast_url)
#     daily = forecast_data.get("daily") or {}
#     times = daily.get("time") or []
#     max_temps = daily.get("temperature_2m_max") or [0 for _ in times]
#     min_temps = daily.get("temperature_2m_min") or [0 for _ in times]
#     rainfalls = daily.get("precipitation_sum") or [0 for _ in times]
#     winds = daily.get("wind_speed_10m_max") or [0 for _ in times]

#     current = forecast_data.get("current") or {}
#     latest_temp = current.get("temperature_2m")
#     latest_humidity = current.get("relative_humidity_2m")
#     latest_rain = current.get("precipitation")
#     latest_wind = current.get("wind_speed_10m")

#     records = []
#     for index, day in enumerate(times):
#         max_temp = max_temps[index] if index < len(max_temps) else 0
#         min_temp = min_temps[index] if index < len(min_temps) else 0
#         avg_temp = ((max_temp or 0) + (min_temp or 0)) / 2
#         rainfall = rainfalls[index] if index < len(rainfalls) else 0
#         wind = winds[index] if index < len(winds) else 0

#         if index == len(times) - 1:
#             temperature_c = latest_temp if latest_temp is not None else avg_temp
#             humidity_pct = latest_humidity if latest_humidity is not None else 60
#             rainfall_mm = latest_rain if latest_rain is not None else rainfall
#             wind_kph = latest_wind if latest_wind is not None else wind
#         else:
#             temperature_c = avg_temp
#             humidity_pct = 60
#             rainfall_mm = rainfall
#             wind_kph = wind

#         summary, action = _build_weather_summary(temperature_c, humidity_pct, rainfall_mm, wind_kph)
#         records.append({
#             "id": index + 1,
#             "farm_id": farm.id,
#             "recorded_at": f"{day}T12:00:00Z",
#             "temperature_c": float(temperature_c),
#             "humidity_pct": float(humidity_pct),
#             "rainfall_mm": float(rainfall_mm),
#             "wind_kph": float(wind_kph),
#             "forecast_summary": summary,
#             "recommended_action": action,
#             "farm_name": farm.name,
#             "farm_location": farm.location,
#             "latitude": latitude,
#             "longitude": longitude,
#         })

#     return records


# # Weather Views

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_weather(request):
#     farm_id = request.query_params.get('farm')

#     if not farm_id:
#         return Response({'detail': 'farm is required.'}, status=status.HTTP_400_BAD_REQUEST)

#     farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)
#     try:
#         return Response(_build_live_weather_records(farm))
#     except Exception as exc:
#         return Response(
#             {'detail': f'Live weather is unavailable for {farm.name}: {exc}'},
#             status=status.HTTP_503_SERVICE_UNAVAILABLE,
#         )


# @api_view(['POST'])
# @permission_classes([IsAdminUser])
# def create_weather(request):
#     serializer = WeatherLogSerializer(data=request.data)
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     weather = serializer.save()
#     out = WeatherLogSerializer(weather)
#     return Response(out.data, status=status.HTTP_201_CREATED)


# @api_view(['GET'])
# def get_weather(request, weather_id):
#     weather = get_object_or_404(WeatherLog, pk=weather_id)
#     serializer = WeatherLogSerializer(weather)
#     return Response(serializer.data)


# @api_view(['PUT'])
# @permission_classes([IsAdminUser])
# def update_weather(request, weather_id):
#     weather = get_object_or_404(WeatherLog, pk=weather_id)
#     serializer = WeatherLogSerializer(weather, data=request.data, partial=True)
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     serializer.save()
#     return Response(serializer.data)


# @api_view(['DELETE'])
# @permission_classes([IsAdminUser])
# def delete_weather(request, weather_id):
#     weather = get_object_or_404(WeatherLog, pk=weather_id)
#     weather.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)








import json
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from farm_overview.models import Farm, WeatherLog
from .serializers import WeatherLogSerializer


# ---------------------------------------------------------
# OpenWeather helpers
# ---------------------------------------------------------

OPENWEATHER_BASE_URL = "https://api.openweathermap.org"
OPENWEATHER_API_KEY = settings.WEATHER_API_KEY


class LocationNotFoundError(ValueError):
    pass


def _fetch_json(url):
    """
    Make a GET request and return the JSON response.
    """
    request = Request(
        url,
        headers={
            "User-Agent": "FarmWeather/1.0",
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _geocode_location(location):
    """
    Convert a farm location into latitude/longitude using
    OpenWeather's Geocoding API.
    """

    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeather API key is not configured.")

    geo_url = (
        f"{OPENWEATHER_BASE_URL}/geo/1.0/direct"
        f"?q={quote(location)}"
        f"&limit=1"
        f"&appid={OPENWEATHER_API_KEY}"
    )

    results = _fetch_json(geo_url)

    if not results:
        raise LocationNotFoundError(
            f"Unable to find coordinates for farm location: {location}"
        )

    place = results[0]

    return {
        "latitude": place["lat"],
        "longitude": place["lon"],
        "name": place.get("name", location),
        "country": place.get("country"),
        "state": place.get("state"),
    }


def _get_current_weather(latitude, longitude):
    """
    Get current weather from OpenWeather.
    """

    url = (
        f"{OPENWEATHER_BASE_URL}/data/2.5/weather"
        f"?lat={latitude}"
        f"&lon={longitude}"
        f"&appid={OPENWEATHER_API_KEY}"
        f"&units=metric"
    )

    return _fetch_json(url)


def _get_forecast(latitude, longitude):
    """
    Get OpenWeather's 5-day / 3-hour forecast.

    This endpoint normally provides up to 5 days of forecast data.
    """

    url = (
        f"{OPENWEATHER_BASE_URL}/data/2.5/forecast"
        f"?lat={latitude}"
        f"&lon={longitude}"
        f"&appid={OPENWEATHER_API_KEY}"
        f"&units=metric"
    )

    return _fetch_json(url)


def _weather_code_description(weather_code):
    if weather_code == 0:
        return "Clear sky"
    if weather_code in (1, 2, 3):
        return "Mainly clear" if weather_code == 1 else "Partly cloudy" if weather_code == 2 else "Overcast"
    if weather_code in (45, 48):
        return "Fog"
    if weather_code in (51, 53, 55, 56, 57):
        return "Drizzle"
    if weather_code in (61, 63, 65, 66, 67):
        return "Rain"
    if weather_code in (71, 73, 75, 77, 85, 86):
        return "Snow"
    if weather_code in (80, 81, 82):
        return "Rain showers"
    if weather_code in (95, 96, 99):
        return "Thunderstorm"
    return "Unknown"


def _extract_hourly_forecasts(hourly_data, now=None, hours=24):
    now = now or datetime.now(timezone.utc)
    times = hourly_data.get("time") or []
    forecast_end = now + timedelta(hours=hours)
    forecasts = []

    for index, timestamp in enumerate(times):
        forecast_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        if forecast_at <= now or forecast_at > forecast_end:
            continue

        def value_for(key):
            values = hourly_data.get(key) or []
            return values[index] if index < len(values) else None

        weather_code = value_for("weather_code")
        forecasts.append({
            "forecast_at": forecast_at.isoformat(),
            "temperature_c": value_for("temperature_2m"),
            "humidity_pct": value_for("relative_humidity_2m"),
            "rainfall_mm": value_for("precipitation") or 0,
            "precipitation_probability_pct": value_for("precipitation_probability") or 0,
            "wind_kph": value_for("wind_speed_10m") or 0,
            "condition": _weather_code_description(weather_code) if weather_code is not None else "Unknown",
        })

    return forecasts


def _geocode_open_meteo_location(location):
    if not location:
        raise LocationNotFoundError("Farm location is missing.")

    geocode_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(location)}&count=1&language=en&format=json"
    )
    results = _fetch_json(geocode_url).get("results") or []
    if not results:
        raise LocationNotFoundError(
            f"Unable to find coordinates for farm location: {location}"
        )

    return results[0]


def _fetch_hourly_forecasts(farm, hours):
    place = _geocode_open_meteo_location((farm.location or "").strip())
    forecast_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={place['latitude']}&longitude={place['longitude']}"
        "&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,"
        "precipitation,wind_speed_10m,weather_code"
        "&forecast_days=2&timezone=UTC&timeformat=unixtime"
    )
    forecast_data = _fetch_json(forecast_url)
    return _extract_hourly_forecasts(
        forecast_data.get("hourly") or {},
        hours=hours,
    )


# ---------------------------------------------------------
# Weather processing
# ---------------------------------------------------------

def _build_weather_summary(
    temperature_c,
    humidity_pct,
    rainfall_mm,
    wind_kph,
):
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
        action = (
            "Planting and field operations can proceed "
            "with normal monitoring."
        )

    else:
        summary = (
            "Conditions are moderate and suitable "
            "for routine field work."
        )
        action = (
            "Continue normal field monitoring "
            "and irrigation planning."
        )

    return summary, action


def _wind_ms_to_kph(wind_speed):
    """
    OpenWeather returns wind speed in m/s when using metric units.
    Convert to km/h to preserve your existing API format.
    """
    if wind_speed is None:
        return 0

    return float(wind_speed) * 3.6


def _group_forecast_by_day(forecast_list):
    """
    Convert OpenWeather's 3-hour forecast entries into
    daily forecast records.

    Each day contains multiple forecast entries. We aggregate
    them into:

    - minimum temperature
    - maximum temperature
    - average humidity
    - total rainfall
    - maximum wind speed
    """

    grouped = {}

    for item in forecast_list:
        timestamp = item.get("dt")

        if not timestamp:
            continue

        forecast_datetime = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )

        day = forecast_datetime.date().isoformat()

        if day not in grouped:
            grouped[day] = {
                "temperatures": [],
                "humidity": [],
                "rainfall": [],
                "wind": [],
                "cloud_cover": [],
                "weather": [],
            }

        main = item.get("main") or {}
        wind = item.get("wind") or {}
        rain = item.get("rain") or {}
        clouds = item.get("clouds") or {}

        temperature = main.get("temp")
        humidity = main.get("humidity")
        wind_speed = wind.get("speed")
        cloud_cover = clouds.get("all")

        # OpenWeather's 3-hour forecast uses rain.3h when available.
        rainfall = rain.get("3h", 0)

        if temperature is not None:
            grouped[day]["temperatures"].append(float(temperature))

        if humidity is not None:
            grouped[day]["humidity"].append(float(humidity))

        if wind_speed is not None:
            grouped[day]["wind"].append(
                _wind_ms_to_kph(wind_speed)
            )

        if cloud_cover is not None:
            grouped[day]["cloud_cover"].append(float(cloud_cover))

        grouped[day]["rainfall"].append(
            float(rainfall or 0)
        )

        weather = item.get("weather") or []

        if weather:
            grouped[day]["weather"].append(
                weather[0]
            )

    return grouped


def _build_live_weather_records(farm):
    """
    Build the weather response expected by the frontend.

    Uses:
        1. OpenWeather Geocoding API
        2. OpenWeather Current Weather API
        3. OpenWeather 5-day Forecast API
    """

    location = (farm.location or "").strip()

    if not location:
        raise LocationNotFoundError("Farm location is missing.")

    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeather API key is not configured.")

    # -----------------------------------------------------
    # 1. Get coordinates
    # -----------------------------------------------------

    place = _geocode_location(location)

    latitude = place["latitude"]
    longitude = place["longitude"]

    # -----------------------------------------------------
    # 2. Get current weather
    # -----------------------------------------------------

    current_data = _get_current_weather(
        latitude,
        longitude,
    )

    current_main = current_data.get("main") or {}
    current_wind = current_data.get("wind") or {}

    current_temperature = current_main.get("temp")
    current_humidity = current_main.get("humidity")
    current_wind_speed = current_wind.get("speed")

    current_wind_kph = _wind_ms_to_kph(
        current_wind_speed
    )

    # Current rainfall.
    #
    # OpenWeather current weather can return:
    # rain.1h
    # rain.3h
    #
    # We prefer 1-hour rainfall when available.
    current_rain = current_data.get("rain") or {}

    current_rainfall = current_rain.get(
        "1h",
        current_rain.get("3h", 0),
    )

    current_rainfall = float(
        current_rainfall or 0
    )

    # -----------------------------------------------------
    # 3. Get forecast
    # -----------------------------------------------------

    forecast_data = _get_forecast(
        latitude,
        longitude,
    )

    forecast_list = forecast_data.get("list") or []

    if not forecast_list:
        raise ValueError(
            "OpenWeather returned no forecast data."
        )

    grouped_forecast = _group_forecast_by_day(
        forecast_list
    )

    records = []

    today = datetime.now(timezone.utc).date().isoformat()

    # -----------------------------------------------------
    # 4. Build frontend-compatible records
    # -----------------------------------------------------

    for index, (day, data) in enumerate(
        sorted(grouped_forecast.items())
    ):
        temperatures = data["temperatures"]
        humidity_values = data["humidity"]
        rainfall_values = data["rainfall"]
        wind_values = data["wind"]
        cloud_cover_values = data["cloud_cover"]

        if not temperatures:
            continue

        min_temp = min(temperatures)
        max_temp = max(temperatures)

        average_temp = (
            min_temp + max_temp
        ) / 2

        average_humidity = (
            sum(humidity_values) / len(humidity_values)
            if humidity_values
            else 60
        )

        total_rainfall = sum(
            rainfall_values
        )

        max_wind = (
            max(wind_values)
            if wind_values
            else 0
        )

        average_cloud_cover = (
            sum(cloud_cover_values) / len(cloud_cover_values)
            if cloud_cover_values
            else None
        )

        if day == today and (current_data.get("clouds") or {}).get("all") is not None:
            average_cloud_cover = float(current_data["clouds"]["all"])

        # For today's record, use the actual current
        # weather rather than the forecast average.
        if day == today:
            temperature_c = (
                float(current_temperature)
                if current_temperature is not None
                else average_temp
            )

            humidity_pct = (
                float(current_humidity)
                if current_humidity is not None
                else average_humidity
            )

            rainfall_mm = current_rainfall

            wind_kph = current_wind_kph

        else:
            temperature_c = average_temp
            humidity_pct = average_humidity
            rainfall_mm = total_rainfall
            wind_kph = max_wind

        summary, action = _build_weather_summary(
            temperature_c,
            humidity_pct,
            rainfall_mm,
            wind_kph,
        )

        records.append(
            {
                "id": index + 1,
                "farm_id": farm.id,

                "recorded_at": f"{day}T12:00:00Z",

                "temperature_c": round(
                    float(temperature_c),
                    2,
                ),

                "humidity_pct": round(
                    float(humidity_pct),
                    2,
                ),

                "rainfall_mm": round(
                    float(rainfall_mm),
                    2,
                ),

                "wind_kph": round(
                    float(wind_kph),
                    2,
                ),

                "cloud_cover_pct": round(average_cloud_cover, 2) if average_cloud_cover is not None else None,
                "clear_sky_pct": round(100 - average_cloud_cover, 2) if average_cloud_cover is not None else None,

                "forecast_summary": summary,
                "recommended_action": action,

                "farm_name": farm.name,
                "farm_location": farm.location,

                "latitude": latitude,
                "longitude": longitude,

                # Extra useful OpenWeather information.
                "weather": (
                    data["weather"][0]
                    if data["weather"]
                    else None
                ),
            }
        )

    return records


# ---------------------------------------------------------
# Weather Views
# ---------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_weather(request):
    farm_id = request.query_params.get("farm")

    if not farm_id:
        return Response(
            {"detail": "farm is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    farm = get_object_or_404(
        Farm,
        pk=farm_id,
        owner=request.user,
    )

    try:
        weather = _build_live_weather_records(farm)

        return Response(weather)

    except LocationNotFoundError as exc:
        return Response(
            {"detail": f"{exc} Enter a city or town and country in the farm location."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def next_hour_weather(request):
    farm_id = request.query_params.get("farm")
    if not farm_id:
        return Response(
            {"detail": "farm is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)

    try:
        forecasts = _fetch_hourly_forecasts(farm, hours=1)
        return Response(forecasts[0] if forecasts else [])
    except LocationNotFoundError as exc:
        return Response(
            {"detail": f"{exc} Enter a city or town and country in the farm location."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def next_24_hours_weather(request):
    farm_id = request.query_params.get("farm")
    if not farm_id:
        return Response(
            {"detail": "farm is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    farm = get_object_or_404(Farm, pk=farm_id, owner=request.user)

    try:
        return Response(_fetch_hourly_forecasts(farm, hours=24))
    except LocationNotFoundError as exc:
        return Response(
            {"detail": f"{exc} Enter a city or town and country in the farm location."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_weather(request):
    serializer = WeatherLogSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    weather = serializer.save()

    out = WeatherLogSerializer(weather)

    return Response(
        out.data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def get_weather(request, weather_id):
    weather = get_object_or_404(
        WeatherLog,
        pk=weather_id,
    )

    serializer = WeatherLogSerializer(weather)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def update_weather(request, weather_id):
    weather = get_object_or_404(
        WeatherLog,
        pk=weather_id,
    )

    serializer = WeatherLogSerializer(
        weather,
        data=request.data,
        partial=True,
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer.save()

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_weather(request, weather_id):
    weather = get_object_or_404(
        WeatherLog,
        pk=weather_id,
    )

    weather.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )