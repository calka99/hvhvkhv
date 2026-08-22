from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from farm_overview.models import Farm, Livestock


class LivestockApiTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(username='owner', password='StrongPass123!')
		self.other_user = user_model.objects.create_user(username='other', password='StrongPass123!')
		self.farm = Farm.objects.create(owner=self.user, name='My Farm', location='Lagos', size_hectares=2)
		self.other_farm = Farm.objects.create(owner=self.other_user, name='Other Farm', location='Abuja', size_hectares=1)
		Livestock.objects.create(farm=self.farm, species='Goat', count=4)
		self.client.force_authenticate(user=self.user)

	def test_list_returns_only_owned_farm_records(self):
		response = self.client.get(reverse('livestock-records'), {'farm_id': self.farm.id})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['species'], 'Goat')

	def test_other_farm_is_not_accessible(self):
		response = self.client.get(reverse('livestock-records'), {'farm_id': self.other_farm.id})

		self.assertEqual(response.status_code, 404)
