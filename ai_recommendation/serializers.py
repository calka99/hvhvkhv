from rest_framework import serializers

from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Recommendation
		fields = [
			'id',
			'farm',
			'month',
			'category',
			'title',
			'message',
			'priority',
			'source_data',
			'created_at',
			'is_active',
		]
		read_only_fields = ['id', 'farm', 'created_at']
