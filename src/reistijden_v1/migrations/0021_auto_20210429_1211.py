# Generated by Django 3.2 on 2021-04-29 12:11

from django.db import migrations


def update_measurement_sites(apps, schema_editor):
    MeasurementLocation = apps.get_model('reistijden_v1', 'MeasurementLocation')

    measurement_locations = MeasurementLocation.objects.all().select_related(
        'measurement'
    )
    for location in measurement_locations:
        location.measurement_site_id = location.measurement.measurement_site_id

    MeasurementLocation.objects.bulk_update(
        measurement_locations, fields=['measurement_site_id'], batch_size=1000
    )


class Migration(migrations.Migration):

    dependencies = [
        ('reistijden_v1', '0020_rename_location_measurementlocation'),
    ]

    operations = [migrations.RunPython(update_measurement_sites)]
