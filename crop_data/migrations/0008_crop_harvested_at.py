from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crop_data', '0007_restore_crop_area_and_planting_density'),
    ]

    operations = [
        migrations.AddField(
            model_name='crop',
            name='harvested_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]