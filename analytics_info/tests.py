from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from farm_overview.models import AnalyticsSnapshot, Farm


class AnalyticsSnapshotAccessTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='snapshot-user', password='StrongPass123!')
		self.farm = Farm.objects.create(owner=self.user, name='Test farm', location='Lagos', size_hectares=1)
		self.snapshot = AnalyticsSnapshot.objects.create(farm=self.farm, period_label='2026-01')
		self.client.force_authenticate(user=self.user)

	def test_regular_user_cannot_list_snapshots(self):
		response = self.client.get(reverse('analytics-list'), {'farm_id': self.farm.id})
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_regular_user_cannot_retrieve_snapshot(self):
		response = self.client.get(reverse('analytics-detail', args=[self.snapshot.id]))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
