from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("farm_overview", "0004_irrigationevent_completed_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="sms_phone_number",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
    ]
