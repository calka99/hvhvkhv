from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from dashboard.models import Dashboard
from farm_overview.models import Farm, SoilReading, WeatherLog


class DashboardOverviewTests(APITestCase):
    def test_dashboard_overview_returns_summary(self):
        user = get_user_model().objects.create_user(
            username='farmowner',
            email='owner@example.com',
            password='strongpass123',
        )

        dashboard = Dashboard.objects.create(owner=user, title='My dashboard')
        farm = Farm.objects.create(
            owner=user,
            name='North Field',
            location='Lagos',
            size_hectares=15.5,
            farm_type='vegetable',
        )
        SoilReading.objects.create(
            farm=farm,
            moisture_pct=45.5,
            ph_level=6.8,
            nitrogen_ppm=30,
            phosphorus_ppm=18,
            potassium_ppm=25,
            organic_matter_pct=2.6,
            degradation_risk='low',
        )
        WeatherLog.objects.create(
            farm=farm,
            temperature_c=29.5,
            humidity_pct=68,
            rainfall_mm=1.2,
            wind_kph=12,
            forecast_summary='Warm and humid',
            recommended_action='Monitor irrigation',
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('dashboard-overview'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], dashboard.title)
        self.assertEqual(response.data['total_farms'], 1)
        self.assertIsNotNone(response.data['latest_soil_reading'])
        self.assertIsNotNone(response.data['latest_weather_log'])
