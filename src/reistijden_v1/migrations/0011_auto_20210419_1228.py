# Generated by Django 3.2 on 2021-04-19 12:28

from django.db import migrations


def create_vehicle_categories(apps, schema_editor):
    VehicleCategory = apps.get_model('reistijden_v1', 'VehicleCategory')
    IndividualTravelTime = apps.get_model('reistijden_v1', 'IndividualTravelTime')
    unique_categories = (
        IndividualTravelTime.objects.all()
        .values_list('old_vehicle_category', flat=True)
        .distinct()
    )

    category_dict = {}

    for category in unique_categories:
        vehicle_category = VehicleCategory.objects.create(name=category)
        category_dict['category'] = vehicle_category.id

    for category, vehicle_category_id in category_dict.items():
        IndividualTravelTime.objects.filter(old_vehicle_category=category).update(
            vehicle_category_id=vehicle_category_id
        )


class Migration(migrations.Migration):

    dependencies = [
        ('reistijden_v1', '0010_auto_20210415_1357'),
    ]

    operations = [
        migrations.RunPython(create_vehicle_categories),
    ]
