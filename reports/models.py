from django.conf import settings
from django.db import models
from django.utils import timezone

from farm_overview.models import Farm


class MonthlyFarmReport(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending recommendation'),
		('reviewed', 'Reviewed'),
	]

	farm = models.ForeignKey(
		Farm,
		on_delete=models.CASCADE,
		related_name='monthly_reports',
	)
	month = models.DateField(help_text='First day of the reporting month.')
	activity_data = models.JSONField(default=dict)
	ai_recommendation = models.TextField(blank=True)
	recommendation_status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default='pending',
	)
	generated_at = models.DateTimeField(default=timezone.now)
	generated_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='generated_monthly_reports',
	)

	class Meta:
		ordering = ['-month', 'farm__name']
		constraints = [
			models.UniqueConstraint(
				fields=['farm', 'month'],
				name='unique_monthly_report_per_farm',
			),
		]

	def __str__(self):
		return f'{self.farm.name} report for {self.month:%Y-%m}'
