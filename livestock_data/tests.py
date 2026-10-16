from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from farm_overview.models import Farm, Livestock
from livestock_data.models import LivestockType


class LivestockApiTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(username='owner', password='StrongPass123!')
		self.other_user = user_model.objects.create_user(username='other', password='StrongPass123!')
		self.farm = Farm.objects.create(owner=self.user, name='My Farm', location='Lagos', size_hectares=2)
		self.other_farm = Farm.objects.create(owner=self.other_user, name='Other Farm', location='Abuja', size_hectares=1)
		Livestock.objects.create(farm=self.farm, species='Goat', count=4)
		self.client.force_authenticate(user=self.user)

	def test_livestock_type_list_includes_available_species(self):
		LivestockType.objects.get_or_create(name='Goat')

		response = self.client.get(reverse('livestock-type-list'))

		self.assertEqual(response.status_code, 200)
		self.assertIn('Goat', [item['name'] for item in response.data])

	def test_list_returns_only_owned_farm_records(self):
		response = self.client.get(reverse('livestock-records'), {'farm_id': self.farm.id})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['species'], 'Goat')

	def test_other_farm_is_not_accessible(self):
		response = self.client.get(reverse('livestock-records'), {'farm_id': self.other_farm.id})

		self.assertEqual(response.status_code, 404)

	def test_cannot_add_livestock_to_crop_only_farm(self):
		crop_farm = Farm.objects.create(
			owner=self.user,
			name='Crop Farm',
			location='Lagos',
			size_hectares=3,
			farm_type='crop',
		)

		response = self.client.post(
			reverse('livestock-records'),
			{'farm_id': crop_farm.id, 'species': 'Goat', 'count': 2},
			format='json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('Create a suitable farm first.', response.data['detail'])
		self.assertFalse(Livestock.objects.filter(farm=crop_farm).exists())

	def test_owner_can_update_livestock_fields_and_farm(self):
		record = Livestock.objects.get(farm=self.farm)
		new_farm = Farm.objects.create(
			owner=self.user,
			name='Second Farm',
			location='Lagos',
			size_hectares=1,
			farm_type='livestock',
		)

		response = self.client.patch(
			reverse('livestock-record-detail', args=[record.id]),
			{
				'farm_id': new_farm.id,
				'species': 'Sheep',
				'tag_id': 'S-12',
				'count': 6,
				'health_status': 'watch',
				'last_vaccination': '2026-04-18T00:00:00Z',
				'feeding_schedule': 'Twice daily',
				'productivity_metric': '2.5 L/day',
			},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		record.refresh_from_db()
		self.assertEqual(record.farm, new_farm)
		self.assertEqual(record.species, 'Sheep')
		self.assertEqual(record.tag_id, 'S-12')
		self.assertEqual(record.count, 6)
		self.assertEqual(record.health_status, 'watch')
		self.assertEqual(record.feeding_schedule, 'Twice daily')
		self.assertEqual(record.productivity_metric, '2.5 L/day')

	def test_cannot_update_another_owners_livestock(self):
		other_record = Livestock.objects.create(farm=self.other_farm, species='Cow')

		response = self.client.patch(
			reverse('livestock-record-detail', args=[other_record.id]),
			{'count': 5},
			format='json',
		)

		self.assertEqual(response.status_code, 404)
		other_record.refresh_from_db()
		self.assertEqual(other_record.count, 1)

	def test_cannot_move_livestock_to_crop_only_farm(self):
		record = Livestock.objects.get(farm=self.farm)
		crop_farm = Farm.objects.create(
			owner=self.user,
			name='Crop Farm',
			location='Lagos',
			size_hectares=3,
			farm_type='crop',
		)

		response = self.client.patch(
			reverse('livestock-record-detail', args=[record.id]),
			{'farm_id': crop_farm.id},
			format='json',
		)

		self.assertEqual(response.status_code, 400)
		record.refresh_from_db()
		self.assertEqual(record.farm, self.farm)


class LivestockHealthAlertApiTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(username='health_owner', password='StrongPass123!')
		self.farm = Farm.objects.create(owner=self.user, name='Dairy Farm', location='Kaduna', size_hectares=4)
		self.livestock = Livestock.objects.create(farm=self.farm, species='Cow', tag_id='C-101', count=3, health_status='watch')
		self.client.force_authenticate(user=self.user)

	def test_create_livestock_health_alert_for_owned_farm(self):
		payload = {
			'farm_id': self.farm.id,
			'livestock_id': self.livestock.id,
			'disease_name': 'Mastitis',
			'severity': 'high',
			'recommended_action': 'Isolate the affected cow and inspect udder health.'
		}

		response = self.client.post(reverse('livestock-health-alerts'), payload, format='json')

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['disease_name'], 'Mastitis')
		self.assertEqual(response.data['farm_name'], self.farm.name)

	def test_list_livestock_health_alerts_filters_to_owner(self):
		response = self.client.get(reverse('livestock-health-alerts'), {'farm_id': self.farm.id})

		self.assertEqual(response.status_code, 200)
		self.assertIsInstance(response.data, list)
