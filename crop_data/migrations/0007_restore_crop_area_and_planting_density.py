from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crop_data', '0006_remove_crop_planting_density_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='crop',
            name='planting_density',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='crop',
            name='area_hectares',
            field=models.FloatField(default=0.0),
        ),
    ]