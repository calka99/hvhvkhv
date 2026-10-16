from django.db import migrations, models


LIVESTOCK_TYPES = [
    "Cattle",
    "Goat",
    "Sheep",
    "Pig",
    "Chicken",
    "Duck",
    "Turkey",
    "Rabbit",
    "Catfish",
    "Tilapia",
    "Snail",
]


def seed_livestock_types(apps, schema_editor):
    LivestockType = apps.get_model("livestock_data", "LivestockType")
    LivestockType.objects.using(schema_editor.connection.alias).bulk_create(
        [LivestockType(name=name) for name in LIVESTOCK_TYPES],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LivestockType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.RunPython(seed_livestock_types, migrations.RunPython.noop),
    ]
