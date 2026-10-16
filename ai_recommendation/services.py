import json
import logging
from urllib.request import Request, urlopen

from urllib.error import HTTPError, URLError
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)


def _validate_ai_recommendations(content):
	parsed = json.loads(content)
	items = parsed.get('recommendations') if isinstance(parsed, dict) else None
	if not isinstance(items, list):
		raise ValueError('AI response must contain a recommendations list.')

	valid_categories = {'general', 'crop', 'irrigation', 'soil', 'weather', 'pest', 'livestock', 'performance'}
	valid_priorities = {'low', 'medium', 'high'}
	validated = []
	for item in items[:8]:
		if not isinstance(item, dict):
			continue
		category = item.get('category')
		title = item.get('title')
		message = item.get('message')
		priority = item.get('priority')
		if (
			category not in valid_categories
			or priority not in valid_priorities
			or not isinstance(title, str)
			or not isinstance(message, str)
			or not title.strip()
			or not message.strip()
		):
			continue
		validated.append({
			'category': category,
			'title': title.strip()[:255],
			'message': message.strip()[:2000],
			'priority': priority,
			'source_data': {},
		})
	if items and not validated:
		raise ValueError('The AI provider returned no valid recommendations.')
	return validated


def generate_ai_recommendations(farm, month, activity_data):
	api_key = settings.GROQ_API_KEY
	if not api_key:
		raise RuntimeError('AI recommendations are not configured. Set GROQ_API_KEY in the backend environment.')

	payload = {
		'model': settings.GROQ_MODEL,
		'messages': [
			{
				'role': 'system',
				'content': (
					'You are a careful farm operations advisor. Make recommendations only for the supplied farm and reporting month. '
					'Use only the supplied activities and measurements from that month. '
					'Do not invent measurements or diagnoses. Return practical farm actions grounded in the observations. '
					'Keep actions specific and prioritized, and limit them to genuine issues or opportunities. '
					'Return an empty recommendations list if the month data does not support a useful action.'
				),
			},
			{
				'role': 'user',
				'content': json.dumps({
					'farm': {
						'name': farm.name,
						'type': farm.farm_type,
						'size_hectares': farm.size_hectares,
					},
					'month': month.strftime('%Y-%m'),
					'monthly_activity_data': activity_data,
				}, cls=DjangoJSONEncoder),
			},
		],
		'response_format': {
			'type': 'json_schema',
			'json_schema': {
				'name': 'farm_recommendations',
				'strict': True,
				'schema': {
					'type': 'object',
					'properties': {
						'recommendations': {
							'type': 'array',
							'items': {
								'type': 'object',
								'properties': {
									'category': {
										'type': 'string',
										'enum': ['general', 'crop', 'irrigation', 'soil', 'weather', 'pest', 'livestock', 'performance'],
									},
									'title': {'type': 'string'},
									'message': {'type': 'string'},
									'priority': {'type': 'string', 'enum': ['low', 'medium', 'high']},
								},
								'required': ['category', 'title', 'message', 'priority'],
								'additionalProperties': False,
							},
						},
					},
					'required': ['recommendations'],
					'additionalProperties': False,
				},
			},
		},
		'temperature': 0.2,
		'max_tokens': 1200,
	}
	request = Request(
		'https://api.groq.com/openai/v1/chat/completions',
		data=json.dumps(payload).encode('utf-8'),
		headers={
			'Authorization': f'Bearer {api_key}',
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			'User-Agent': 'FarmOS/1.0',
		},
		method='POST',
	)
	try:
		with urlopen(request, timeout=20) as response:
			result = json.loads(response.read().decode('utf-8'))
	except (HTTPError, URLError) as e:
		logger.error(f"Error occurred while fetching AI recommendations: {e}")
		raise RuntimeError('Failed to fetch AI recommendations.')
	content = result['choices'][0]['message']['content']
	recommendations = _validate_ai_recommendations(content)
	return recommendations