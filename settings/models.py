from django.conf import settings
from django.db import models


class FarmPreference(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farm_preference',
    )
    ai_recommendations_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'Farm preferences for {self.owner}'
