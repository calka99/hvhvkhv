from django.db import models

from farm_overview.models import Farm


class Recommendation(models.Model):
	PRIORITY_CHOICES = [
		('low', 'Low'),
		('medium', 'Medium'),
		('high', 'High'),
	]

	farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='recommendations')
	category = models.CharField(max_length=50)
	title = models.CharField(max_length=255)
	message = models.TextField()
	priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
	source_data = models.JSONField(default=dict)
	created_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.title} for {self.farm.name}'
