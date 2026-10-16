import json
from datetime import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from farm_overview.models import Farm, SoilReading
from settings.models import FarmPreference
from .models import Recommendation
from .services import generate_ai_recommendations


@override_settings(GROQ_API_KEY='test-groq-key')
class RecommendationTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(
			username='recommendation-owner',
			password='StrongPass123!',
		)
		self.other_user = user_model.objects.create_user(
			username='other-owner',
			password='StrongPass123!',
		)
		self.farm = Farm.objects.create(
			owner=self.user,
			name='Test Farm',
			location='Lagos',
			size_hectares=2,
		)
		self.client.force_authenticate(user=self.user)
		self.month = '2026-08'
		self.month_date = datetime.strptime(self.month, '%Y-%m').date().replace(day=1)

	def create_soil_reading(self, farm, month='2026-08'):
		recorded_at = timezone.make_aware(datetime.strptime(f'{month}-10', '%Y-%m-%d'))
		return SoilReading.objects.create(
			farm=farm,
			recorded_at=recorded_at,
			moisture_pct=20,
			ph_level=6.5,
		)

	def test_recommendations_endpoint_does_not_list_cards(self):
		response = self.client.get(reverse('recommendations'))

		self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

	@patch('ai_recommendation.views.generate_ai_recommendations')
	def test_post_generates_only_for_selected_owned_farm(self, generate_ai):
		second_farm = Farm.objects.create(
			owner=self.user,
			name='Second Farm',
			location='Abuja',
			size_hectares=1,
		)
		self.create_soil_reading(self.farm)
		self.create_soil_reading(second_farm)
		generate_ai.return_value = [{
			'category': 'soil',
			'title': 'Review soil readings',
			'message': 'Review this month’s soil readings.',
			'priority': 'low',
			'source_data': {},
		}]

		response = self.client.post(
			reverse('recommendations'),
			{'month': self.month, 'farm_id': self.farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data['farm_id'], self.farm.id)
		self.assertEqual(response.data['farm_name'], self.farm.name)
		self.assertEqual(response.data['month'], self.month_date.isoformat())
		self.assertEqual(response.data['recommendation_count'], 1)
		self.assertEqual(response.data['status'], 'generated')
		generate_ai.assert_called_once()
		self.assertEqual(
			Recommendation.objects.filter(farm=self.farm, month=self.month_date).count(),
			1,
		)
		self.assertEqual(
			Recommendation.objects.filter(farm=second_farm, month=self.month_date).count(),
			0,
		)

	def test_post_rejects_farm_owned_by_another_user(self):
		other_farm = Farm.objects.create(
			owner=self.other_user,
			name='Private Farm',
			location='Kano',
			size_hectares=1,
		)

		response = self.client.post(
			reverse('recommendations'),
			{'month': self.month, 'farm_id': other_farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_post_requires_selected_farm(self):
		response = self.client.post(
			reverse('recommendations'),
			{'month': self.month},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('Select a farm', response.data['detail'])

	@patch('ai_recommendation.views.generate_ai_recommendations')
	def test_no_monthly_activity_does_not_call_ai(self, generate_ai):
		response = self.client.post(
			reverse('recommendations'),
			{'month': self.month, 'farm_id': self.farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['farm_id'], self.farm.id)
		self.assertEqual(response.data['status'], 'no_activity')
		self.assertEqual(response.data['recommendation_count'], 0)
		generate_ai.assert_not_called()

	@patch('ai_recommendation.views.generate_ai_recommendations')
	def test_disabled_selected_farm_is_not_generated(self, generate_ai):
		second_farm = Farm.objects.create(
			owner=self.user,
			name='Second Farm',
			location='Abuja',
			size_hectares=1,
		)
		FarmPreference.objects.create(owner=self.user, ai_recommendations_enabled=False)
		self.create_soil_reading(self.farm)
		self.create_soil_reading(second_farm)
		generate_ai.return_value = [{
			'category': 'soil',
			'title': 'Review soil readings',
			'message': 'Review this month’s soil readings.',
			'priority': 'low',
			'source_data': {},
		}]

		response = self.client.post(
			reverse('recommendations'),
			{'month': self.month, 'farm_id': self.farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertIn('disabled', response.data['detail'])
		generate_ai.assert_not_called()

	def test_invalid_month_is_rejected(self):
		response = self.client.post(
			reverse('recommendations'),
			{'month': 'August 2026', 'farm_id': self.farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	@override_settings(GROQ_API_KEY='')
	def test_generation_without_api_key_returns_error_if_month_has_activity(self):
		self.create_soil_reading(self.farm)

		response = self.client.post(
			reverse('recommendations'),
			{'month': self.month, 'farm_id': self.farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
		self.assertIn('GROQ_API_KEY', response.data['detail'])

	@patch('ai_recommendation.services.urlopen')
	def test_groq_request_receives_only_the_selected_month_activity(self, mock_urlopen):
		mock_response = mock_urlopen.return_value.__enter__.return_value
		mock_response.read.return_value = json.dumps({
			'choices': [{
				'message': {
					'content': json.dumps({
						'recommendations': [{
							'category': 'soil',
							'title': 'Check soil moisture',
							'message': 'Review the soil readings recorded this month.',
							'priority': 'medium',
						}],
					}),
				},
			}],
		}).encode()
		activity_data = {
			'period': {'month': self.month},
			'activity_counts': {'soil_readings': 1},
			'activities': {'soil_readings': [{'moisture_pct': 20}]},
		}

		recommendations = generate_ai_recommendations(self.farm, self.month_date, activity_data)

		self.assertEqual(recommendations[0]['title'], 'Check soil moisture')
		request = mock_urlopen.call_args.args[0]
		self.assertEqual(request.full_url, 'https://api.groq.com/openai/v1/chat/completions')
		payload = json.loads(request.data)
		input_data = json.loads(payload['messages'][1]['content'])
		self.assertEqual(input_data['month'], self.month)
		self.assertEqual(input_data['monthly_activity_data'], activity_data)
		self.assertEqual(payload['response_format']['type'], 'json_schema')
