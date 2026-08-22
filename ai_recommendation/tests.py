from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from farm_overview.models import Farm, SoilReading


class RecommendationTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='recommendation-owner',
			password='StrongPass123!',
		)
		self.other_user = get_user_model().objects.create_user(
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

	def test_get_generates_recommendation_from_dry_soil(self):
		SoilReading.objects.create(farm=self.farm, moisture_pct=20, ph_level=6.5)

		response = self.client.get(reverse('recommendations'), {'farm_id': self.farm.id})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data[0]['category'], 'irrigation')
		self.assertEqual(response.data[0]['priority'], 'high')

	def test_other_users_cannot_access_farm_recommendations(self):
		other_farm = Farm.objects.create(
			owner=self.other_user,
			name='Other Farm',
			location='Abuja',
			size_hectares=1,
		)

		response = self.client.get(reverse('recommendations'), {'farm_id': other_farm.id})

		self.assertEqual(response.status_code, 404)
