from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('ai_recommendation', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='recommendation',
			name='month',
			field=models.DateField(blank=True, db_index=True, null=True),
		),
	]
