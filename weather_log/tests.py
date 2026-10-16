from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.test import TestCase

from .views import _extract_hourly_forecasts, _geocode_open_meteo_location


class NextHourForecastTests(TestCase):
    @patch("weather_log.views._fetch_json")
    def test_geocodes_farm_location_with_open_meteo(self, fetch_json):
        fetch_json.return_value = {
            "results": [{"latitude": 4.8, "longitude": 7.0}],
        }

        place = _geocode_open_meteo_location("Port Harcourt, Nigeria")

        self.assertEqual(place["latitude"], 4.8)
        self.assertEqual(place["longitude"], 7.0)
        self.assertIn("geocoding-api.open-meteo.com", fetch_json.call_args.args[0])

    def test_returns_the_first_hourly_forecast_after_now(self):
        now = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
        hourly_data = {
            "time": [
                int((now - timedelta(hours=1)).timestamp()),
                int((now + timedelta(hours=1)).timestamp()),
                int((now + timedelta(hours=2)).timestamp()),
            ],
            "temperature_2m": [21, 23.5, 25],
            "relative_humidity_2m": [75, 70, 65],
            "precipitation_probability": [10, 25, 35],
            "precipitation": [0, 0.4, 0.8],
            "wind_speed_10m": [5, 7.2, 10],
            "weather_code": [0, 61, 3],
        }

        forecasts = _extract_hourly_forecasts(hourly_data, now=now, hours=1)

        self.assertEqual(len(forecasts), 1)
        self.assertEqual(forecasts[0]["forecast_at"], (now + timedelta(hours=1)).isoformat())
        self.assertEqual(forecasts[0]["temperature_c"], 23.5)
        self.assertEqual(forecasts[0]["condition"], "Rain")
        self.assertEqual(forecasts[0]["rainfall_mm"], 0.4)
        self.assertEqual(forecasts[0]["precipitation_probability_pct"], 25)
        self.assertEqual(forecasts[0]["wind_kph"], 7.2)

    def test_omits_forecasts_outside_the_requested_window(self):
        now = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
        hourly_data = {
            "time": [
                int((now - timedelta(hours=1)).timestamp()),
                int((now + timedelta(hours=2)).timestamp()),
            ],
            "temperature_2m": [20, 24],
        }

        forecasts = _extract_hourly_forecasts(hourly_data, now=now, hours=1)

        self.assertEqual(forecasts, [])
