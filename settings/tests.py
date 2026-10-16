from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from farm_overview.models import Farm
from settings.models import FarmPreference


class OwnerFarmSettingsApiTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.owner = user_model.objects.create_user(
			username='settings_owner',
			password='StrongPass123!',
		)
		self.other_user = user_model.objects.create_user(
			username='settings_other',
			password='StrongPass123!',
		)
		self.farm = Farm.objects.create(
			owner=self.owner,
			name='Owner Farm',
			location='Lagos',
			size_hectares=2,
		)
		self.second_farm = Farm.objects.create(
			owner=self.owner,
			name='Second Owner Farm',
			location='Abuja',
			size_hectares=3,
		)

	def test_owner_can_load_and_update_settings_for_all_owned_farms(self):
		self.client.force_authenticate(self.owner)

		get_response = self.client.get(reverse('settings-detail'))
		self.assertEqual(get_response.status_code, 200)
		self.assertTrue(get_response.data['ai_recommendations_enabled'])
		self.assertEqual(FarmPreference.objects.filter(owner=self.owner).count(), 1)

		update_response = self.client.put(
			reverse('settings-update'),
			{'ai_recommendations_enabled': False},
			format='json',
		)

		self.assertEqual(update_response.status_code, 200)
		self.assertFalse(update_response.data['ai_recommendations_enabled'])
		self.assertFalse(FarmPreference.objects.get(owner=self.owner).ai_recommendations_enabled)

	def test_user_preferences_are_isolated_between_owners(self):
		self.client.force_authenticate(self.other_user)

		get_response = self.client.get(reverse('settings-detail'))
		update_response = self.client.put(
			reverse('settings-update'),
			{'ai_recommendations_enabled': False},
			format='json',
		)

		self.assertEqual(get_response.status_code, 200)
		self.assertEqual(update_response.status_code, 200)
		self.assertFalse(update_response.data['ai_recommendations_enabled'])
		self.assertTrue(FarmPreference.objects.get(owner=self.owner).ai_recommendations_enabled)

	def test_update_rejects_missing_or_non_boolean_value(self):
		self.client.force_authenticate(self.owner)

		response = self.client.put(reverse('settings-update'), {'ai_recommendations_enabled': 'not-a-boolean'}, format='json')

		self.assertEqual(response.status_code, 400)
