# Generated by Django 3.2.14 on 2022-07-30 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reistijden_v1', '0009_fix_field_rename'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasurementSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_id', models.CharField(help_text='The measurementsitereference element describes the measurement site (section or trajectory) against which the values are reported', max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('name', models.CharField(help_text='An optional readable name for the measurement site.', max_length=255, null=True)),
                ('type', models.CharField(help_text='\n        Measurement site type. A measurement site can be either a location, a section\n        or a trajectory.\n        - Location\n        A location refers to a point location in the road network from which data\n        (vehicle passages) are collected.  A location consists of one or more\n        camera-lane pairs. The Amsterdam Travel time system delivers vehicle count\n        per location per lane per vehicle category under the trafficflow publication.\n        - Section\n        A section refers to a traversible route between two locations.\n        The Amsterdam Travel time system delivers the following for the sections\n        defined in the system:\n        a. Raw, representative and processed travel time values under the traveltime\n           publication.\n        b. Individual travel time values under the individualtraveltime publication\n        - Trajectory\n        A trajectory refers to a traversible route created using one or more sections.\n        The Amsterdam Travel time system delivers the following for the trajectories\n        defined in the system:\n        a. Processed, predicted and actual under the traveltime publication.\n        ', max_length=255)),
                ('length', models.IntegerField(help_text='This element contains information about the length (in meters) of the measurement site. Applicable only for sections and trajectories', null=True)),
                ('measurement_site_json', models.JSONField(help_text='This field is made to include a nested json object containing the measurement site meta data and locations, its lanes and its respective cameras. If something changes in the measurement site or any of the locations, lanes or cameras, new records need to be created for all of them. To be able to test this somewhat easily, we create a json object in this field to be able to test for changes in any of those objects by doing a select on all fields of the measurement site, including this locations_json. Note that the order of keys in the json objects does not matter when using a native jsonb field.', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Measurement2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurement_site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reistijden_v1.measurementsite')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reistijden_v1.publication')),
            ],
        ),
    ]
