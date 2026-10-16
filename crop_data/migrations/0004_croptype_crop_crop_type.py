from django.db import migrations, models
import django.db.models.deletion


def create_initial_crop_types(apps, schema_editor):
    Category = apps.get_model('crop_data', 'Category')
    CropType = apps.get_model('crop_data', 'CropType')
    Crop = apps.get_model('crop_data', 'Crop')

    for category in Category.objects.all():
        crop_type, _ = CropType.objects.get_or_create(
            category_id=category.id,
            name=category.name,
            defaults={'lifespan_days': category.lifespan_days},
        )
        Crop.objects.filter(category_id=category.id, crop_type__isnull=True).update(crop_type_id=crop_type.id)


class Migration(migrations.Migration):

    dependencies = [
        ('crop_data', '0003_category_lifespan_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='CropType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('lifespan_days', models.PositiveIntegerField(default=90)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crop_types', to='crop_data.category')),
            ],
            options={
                'ordering': ['category__name', 'name'],
            },
        ),
        migrations.AddField(
            model_name='crop',
            name='crop_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='crops', to='crop_data.croptype'),
        ),
        migrations.AddConstraint(
            model_name='croptype',
            constraint=models.UniqueConstraint(fields=('category', 'name'), name='unique_crop_type_per_category'),
        ),
        migrations.RunPython(create_initial_crop_types, migrations.RunPython.noop),
    ]
