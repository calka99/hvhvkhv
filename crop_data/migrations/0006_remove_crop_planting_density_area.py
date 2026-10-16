from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crop_data', '0005_seed_crop_types'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crop',
            name='planting_density',
        ),
        migrations.RemoveField(
            model_name='crop',
            name='area_hectares',
        ),
    ]
