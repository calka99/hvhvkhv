from datetime import date
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from farm_overview.models import Farm
from .models import Category, Crop, CropType


class CropCreateTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='newfarmer',
			email='newfarmer@example.com',
			password='StrongPass123!',
		)
		self.farm = Farm.objects.create(
			owner=self.user,
			name='New Farm',
			location='Farm location',
			size_hectares=2.5,
		)
		category = Category.objects.create(name='Vegetables')
		self.crop_type = CropType.objects.create(
			category=category,
			name='Tomato',
			lifespan_days=90,
		)
		self.client.force_authenticate(user=self.user)

	def test_create_crop_for_owned_farm(self):
		response = self.client.post(
			reverse('crop-create'),
			{
				'farm_id': self.farm.id,
				'crop_type_id': self.crop_type.id,
				'variety': 'Roma',
				'planting_date': '2026-10-01T00:00:00Z',
				'area_hectares': 1.25,
				'planting_density': '40,000 plants/ha',
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
		crop = Crop.objects.get(pk=response.data['id'])
		self.assertEqual(crop.farm, self.farm)
		self.assertEqual(crop.crop_type, self.crop_type)
		self.assertEqual(crop.area_hectares, 1.25)
		self.assertEqual(crop.planting_density, '40,000 plants/ha')
		self.assertEqual(crop.expected_harvest_date.date(), date(2026, 12, 30))

	def test_owner_can_mark_crop_harvested(self):
		crop = Crop.objects.create(
			farm=self.farm,
			category=self.crop_type.category,
			crop_type=self.crop_type,
			name=self.crop_type.name,
			planting_date='2026-07-01T00:00:00Z',
			expected_harvest_date=timezone.now() - timedelta(days=1),
		)

		response = self.client.post(
			reverse('crop-harvest', args=[crop.id]),
			{'historical_yield_kg': 124.5},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		crop.refresh_from_db()
		self.assertEqual(crop.growth_stage, 'harvested')
		self.assertIsNotNone(crop.harvested_at)
		self.assertEqual(crop.historical_yield_kg, 124.5)
		self.assertEqual(response.data['growth_stage'], 'harvested')

	def test_harvest_requires_non_negative_yield(self):
		crop = Crop.objects.create(
			farm=self.farm,
			category=self.crop_type.category,
			crop_type=self.crop_type,
			name=self.crop_type.name,
		)

		response = self.client.post(
			reverse('crop-harvest', args=[crop.id]),
			{'historical_yield_kg': -2},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		crop.refresh_from_db()
		self.assertNotEqual(crop.growth_stage, 'harvested')
		self.assertIsNone(crop.harvested_at)

	def test_owner_cannot_harvest_before_expected_harvest_date(self):
		crop = Crop.objects.create(
			farm=self.farm,
			category=self.crop_type.category,
			crop_type=self.crop_type,
			name=self.crop_type.name,
			expected_harvest_date=timezone.now() + timedelta(days=1),
		)

		response = self.client.post(
			reverse('crop-harvest', args=[crop.id]),
			{'historical_yield_kg': 124.5},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		crop.refresh_from_db()
		self.assertIsNone(crop.harvested_at)
		self.assertNotEqual(crop.growth_stage, 'harvested')

	def test_user_cannot_mark_another_farm_crop_harvested(self):
		other_user = get_user_model().objects.create_user(
			username='otherfarmer',
			password='StrongPass123!',
		)
		crop = Crop.objects.create(
			farm=self.farm,
			category=self.crop_type.category,
			crop_type=self.crop_type,
			name=self.crop_type.name,
		)
		self.client.force_authenticate(user=other_user)

		response = self.client.post(
			reverse('crop-harvest', args=[crop.id]),
			{'historical_yield_kg': 100},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		crop.refresh_from_db()
		self.assertIsNone(crop.harvested_at)

	def test_owner_can_delete_crop(self):
		crop = Crop.objects.create(
			farm=self.farm,
			category=self.crop_type.category,
			crop_type=self.crop_type,
			name=self.crop_type.name,
		)

		response = self.client.delete(reverse('crop-delete', args=[crop.id]))

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Crop.objects.filter(pk=crop.id).exists())

	def test_user_cannot_delete_another_farm_crop(self):
		other_user = get_user_model().objects.create_user(
			username='cropdeleteother',
			password='StrongPass123!',
		)
		crop = Crop.objects.create(
			farm=self.farm,
			category=self.crop_type.category,
			crop_type=self.crop_type,
			name=self.crop_type.name,
		)
		self.client.force_authenticate(user=other_user)

		response = self.client.delete(reverse('crop-delete', args=[crop.id]))

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertTrue(Crop.objects.filter(pk=crop.id).exists())
