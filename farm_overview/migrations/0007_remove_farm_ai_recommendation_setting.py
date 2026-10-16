from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farm_overview', '0006_remove_sms_settings'),
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='settings',
            name='ai_recommendations_enabled',
        ),
    ]
