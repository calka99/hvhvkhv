from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from crop_data.models import Crop
from .models import Farm


class FarmUpdateTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.owner = user_model.objects.create_user(username='owner', password='StrongPass123!')
		self.other_user = user_model.objects.create_user(username='other', password='StrongPass123!')
		self.farm = Farm.objects.create(
			owner=self.owner,
			name='Original farm',
			location='Original location',
			size_hectares=2.0,
			farm_type='mixed',
		)

	def test_owner_can_update_all_farm_creation_fields(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.put(
			reverse('farm-update', args=[self.farm.id]),
			{
				'name': 'Updated farm',
				'location': 'Port Harcourt, Nigeria',
				'size_hectares': 3.5,
				'farm_type': 'crop',
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.farm.refresh_from_db()
		self.assertEqual(self.farm.name, 'Updated farm')
		self.assertEqual(self.farm.location, 'Port Harcourt, Nigeria')
		self.assertEqual(self.farm.size_hectares, 3.5)
		self.assertEqual(self.farm.farm_type, 'crop')

	def test_user_cannot_update_another_users_farm(self):
		self.client.force_authenticate(user=self.other_user)
		response = self.client.put(
			reverse('farm-update', args=[self.farm.id]),
			{
				'name': 'Hijacked farm',
				'location': 'Elsewhere',
				'size_hectares': 8,
				'farm_type': 'livestock',
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.farm.refresh_from_db()
		self.assertEqual(self.farm.name, 'Original farm')

	def test_owner_can_delete_farm(self):
		self.client.force_authenticate(user=self.owner)

		response = self.client.delete(reverse('farm-delete', args=[self.farm.id]))

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Farm.objects.filter(pk=self.farm.id).exists())

	def test_user_cannot_delete_another_users_farm(self):
		self.client.force_authenticate(user=self.other_user)

		response = self.client.delete(reverse('farm-delete', args=[self.farm.id]))

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertTrue(Farm.objects.filter(pk=self.farm.id).exists())


class FarmOverviewYieldTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='yieldfarmer',
			password='StrongPass123!',
		)
		self.farm = Farm.objects.create(
			owner=self.user,
			name='Yield farm',
			location='Farm location',
			size_hectares=2.0,
		)
		self.other_farm = Farm.objects.create(
			owner=self.user,
			name='Other farm',
			location='Other location',
			size_hectares=1.0,
		)
		self.client.force_authenticate(user=self.user)

	def test_overview_sums_entered_yield_for_its_farm(self):
		Crop.objects.create(
			farm=self.farm,
			name='Tomato',
			historical_yield_kg=1250.5,
		)
		Crop.objects.create(
			farm=self.farm,
			name='Pepper',
			historical_yield_kg=700,
		)
		Crop.objects.create(
			farm=self.farm,
			name='Maize',
		)
		Crop.objects.create(
			farm=self.other_farm,
			name='Cassava',
			historical_yield_kg=9000,
		)

		response = self.client.get(reverse('farm-overview', args=[self.farm.id]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['total_crop_yield_kg'], 1950.5)

	def test_overview_reports_zero_when_no_yield_has_been_entered(self):
		response = self.client.get(reverse('farm-overview', args=[self.farm.id]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['total_crop_yield_kg'], 0)

	def test_owner_can_list_only_their_farms_for_recommendation_selection(self):
		other_user = get_user_model().objects.create_user(
			username='anotherfarmer',
			password='StrongPass123!',
		)
		Farm.objects.create(
			owner=other_user,
			name='Private farm',
			location='Private location',
			size_hectares=5,
		)

		response = self.client.get(reverse('farm-owned-list'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(
			response.data,
			[
				{'id': self.other_farm.id, 'name': self.other_farm.name},
				{'id': self.farm.id, 'name': self.farm.name},
			],
		)
