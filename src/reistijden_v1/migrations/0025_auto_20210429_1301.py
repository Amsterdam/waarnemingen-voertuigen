# Generated by Django 3.2 on 2021-04-29 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reistijden_v1', '0024_auto_20210429_1255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lane',
            name='camera_id',
        ),
        migrations.RemoveField(
            model_name='lane',
            name='lane_number',
        ),
        migrations.RemoveField(
            model_name='lane',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='lane',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='lane',
            name='status',
        ),
        migrations.RemoveField(
            model_name='lane',
            name='view_direction',
        ),
        migrations.AlterField(
            model_name='lane',
            name='specific_lane',
            field=models.CharField(help_text='Indicative name for the lane (lane1, lane2, lane3 … lane9 etc) used in the Amsterdam Travel Time system. The actual lane number is available at Camera.lane_number with respect to the camera view direction at the measurement location.', max_length=255),
        ),
    ]