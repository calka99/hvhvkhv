from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("farm_overview", "0005_settings_sms_phone_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="settings",
            name="sms_phone_number",
        ),
        migrations.RemoveField(
            model_name="settings",
            name="sms_alerts_enabled",
        ),
    ]
