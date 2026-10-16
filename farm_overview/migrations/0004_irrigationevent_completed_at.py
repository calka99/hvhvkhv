from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("farm_overview", "0003_livestockhealthalert"),
    ]

    operations = [
        migrations.AddField(
            model_name="irrigationevent",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
