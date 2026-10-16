from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from farm_overview.models import Farm, IrrigationEvent


class IrrigationCompletionTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="irrigation_owner",
            password="StrongPass123!",
        )
        self.farm = Farm.objects.create(
            owner=self.user,
            name="Irrigation farm",
            location="Lagos",
            size_hectares=2,
        )
        self.event = IrrigationEvent.objects.create(
            farm=self.farm,
            zone="North field",
            scheduled_at=timezone.now(),
        )
        self.client.force_authenticate(user=self.user)

    def test_completing_event_records_completion_time(self):
        response = self.client.patch(
            reverse("irrigation-status", args=[self.event.id]),
            {"status": "completed"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, "completed")
        self.assertIsNotNone(self.event.completed_at)
        self.assertIsNotNone(response.data["completed_at"])

    def test_reopening_event_clears_completion_time(self):
        self.event.status = "completed"
        self.event.completed_at = timezone.now() - timedelta(days=1)
        self.event.save()

        response = self.client.patch(
            reverse("irrigation-status", args=[self.event.id]),
            {"status": "scheduled"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, "scheduled")
        self.assertIsNone(self.event.completed_at)
