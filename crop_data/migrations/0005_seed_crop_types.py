from django.db import migrations


CROP_TYPES = {
    'tube': [
        ('Potato', 90),
        ('Yam', 180),
        ('Cassava', 270),
    ],
    'cereal crop': [
        ('Rice', 120),
        ('Maize', 100),
    ],
}


def seed_crop_types(apps, schema_editor):
    Category = apps.get_model('crop_data', 'Category')
    CropType = apps.get_model('crop_data', 'CropType')
    Crop = apps.get_model('crop_data', 'Crop')

    for category_name, crop_types in CROP_TYPES.items():
        category = Category.objects.filter(name__iexact=category_name).first()
        if not category:
            continue

        for name, lifespan_days in crop_types:
            CropType.objects.get_or_create(
                category_id=category.id,
                name=name,
                defaults={'lifespan_days': lifespan_days},
            )

        legacy_type = CropType.objects.filter(
            category_id=category.id,
            name__iexact=category.name,
        ).first()
        if legacy_type and not Crop.objects.filter(crop_type_id=legacy_type.id).exists():
            legacy_type.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crop_data', '0004_croptype_crop_crop_type'),
    ]

    operations = [
        migrations.RunPython(seed_crop_types, migrations.RunPython.noop),
    ]
