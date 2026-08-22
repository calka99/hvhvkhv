from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from farm_overview.models import MarketPrice


class MarketDataApiTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='viewer', password='StrongPass123!')
		self.client.force_authenticate(user=self.user)

	def test_authenticated_user_can_list_market_prices(self):
		MarketPrice.objects.create(
			commodity='Maize', region='Lagos', price_per_kg=120, currency='NGN',
		)

		response = self.client.get(reverse('market-prices'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data[0]['commodity'], 'Maize')

	def test_non_admin_cannot_create_market_price(self):
		response = self.client.post(reverse('market-prices'), {
			'commodity': 'Rice', 'region': 'Lagos', 'price_per_kg': 300,
		}, format='json')

		self.assertEqual(response.status_code, 403)
