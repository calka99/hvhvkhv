from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_owner_preferences(apps, schema_editor):
    Farm = apps.get_model('farm_overview', 'Farm')
    FarmSettings = apps.get_model('farm_overview', 'Settings')
    FarmPreference = apps.get_model('settings', 'FarmPreference')
    database = schema_editor.connection.alias
    owner_ids = Farm.objects.using(database).values_list('owner_id', flat=True).distinct()
    for owner_id in owner_ids.iterator():
        farm_settings = FarmSettings.objects.using(database).filter(farm__owner_id=owner_id)
        enabled = not farm_settings.filter(ai_recommendations_enabled=False).exists()
        FarmPreference.objects.using(database).create(
            owner_id=owner_id,
            ai_recommendations_enabled=enabled,
        )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('farm_overview', '0006_remove_sms_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='FarmPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ai_recommendations_enabled', models.BooleanField(default=True)),
                ('owner', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='farm_preference',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.RunPython(create_owner_preferences, migrations.RunPython.noop),
    ]
