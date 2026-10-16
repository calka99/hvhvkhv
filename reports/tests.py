from datetime import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from farm_overview.models import Farm, IrrigationEvent, SoilReading


User = get_user_model()


class MonthlyFarmReportTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_superuser(
			username='admin',
			email='admin@example.com',
			password='StrongPass123!',
		)
		self.farm = Farm.objects.create(
			owner=self.admin,
			name='Test Farm',
			location='Abuja',
			size_hectares=4,
		)
		self.month_start = timezone.make_aware(datetime(2026, 8, 1))
		SoilReading.objects.create(
			farm=self.farm,
			recorded_at=self.month_start,
			moisture_pct=25,
			ph_level=6.2,
		)
		IrrigationEvent.objects.create(
			farm=self.farm,
			zone='North',
			scheduled_at=self.month_start,
			duration_minutes=20,
			status='completed',
		)
		self.client.force_authenticate(self.admin)

	def test_generate_monthly_report_contains_structured_activity_feedback(self):
		response = self.client.post(
			reverse('monthly-report-generate'),
			{'month': '2026-08', 'farm_id': self.farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, 201)
		report = response.data[0]
		self.assertEqual(report['activity_data']['activity_counts']['soil_readings'], 1)
		self.assertEqual(report['activity_data']['measurements']['irrigation_minutes'], 20)
		self.assertIn('Average soil moisture is below 30%; review irrigation planning.', report['activity_data']['feedback_signals'])

	def test_invalid_month_is_rejected(self):
		response = self.client.post(
			reverse('monthly-report-generate'),
			{'month': 'August 2026'},
			format='json',
		)

		self.assertEqual(response.status_code, 400)

	def test_regular_user_can_generate_reports_for_all_owned_farms_only(self):
		self.client.post(
			reverse('monthly-report-generate'),
			{'month': '2026-08', 'farm_id': self.farm.id},
			format='json',
		)
		owner = User.objects.create_user(
			username='farm_owner',
			email='owner@example.com',
			password='StrongPass123!',
		)
		owned_farm = Farm.objects.create(
			owner=owner,
			name='Owner Farm',
			location='Lagos',
			size_hectares=2,
		)
		Farm.objects.create(
			owner=self.admin,
			name='Another Owner Farm',
			location='Kano',
			size_hectares=3,
		)
		self.client.force_authenticate(owner)

		response = self.client.post(
			reverse('monthly-report-generate'),
			{'month': '2026-08'},
			format='json',
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual([report['farm'] for report in response.data], [owned_farm.id])

		list_response = self.client.get(reverse('monthly-report-list'))

		self.assertEqual(list_response.status_code, 200)
		self.assertEqual([report['farm'] for report in list_response.data], [owned_farm.id])

		other_farm_response = self.client.get(
			reverse('monthly-report-list'),
			{'farm_id': self.farm.id},
		)
		self.assertEqual(other_farm_response.status_code, 404)

	def test_owner_cannot_generate_report_for_another_users_farm(self):
		owner = User.objects.create_user(
			username='limited_owner',
			email='limited@example.com',
			password='StrongPass123!',
		)
		self.client.force_authenticate(owner)

		response = self.client.post(
			reverse('monthly-report-generate'),
			{'month': '2026-08', 'farm_id': self.farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, 404)
