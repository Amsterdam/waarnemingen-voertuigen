# Generated by Django 3.2 on 2021-04-29 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reistijden_v1', '0019_remove_trafficflowcategorycount_type'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Location',
            new_name='MeasurementLocation',
        ),
        migrations.AlterField(
            model_name='measurementlocation',
            name='index',
            field=models.IntegerField(help_text="The index attribute indicates the order of measurement location in the measurement site. Optional, if the measurement site is of type 'location'", null=True),
        ),
        migrations.RenameField(
            model_name='lane',
            old_name='location',
            new_name='measurement_location',
        ),
        migrations.AddField(
            model_name='measurementlocation',
            name='measurement_site',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reistijden_v1.measurementsite'),
        ),
    ]
