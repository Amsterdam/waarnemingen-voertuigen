# Generated by Django 3.1 on 2020-08-12 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reistijden_v1', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='camera_id',
        ),
        migrations.RemoveField(
            model_name='location',
            name='lane_number',
        ),
        migrations.RemoveField(
            model_name='location',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='location',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='location',
            name='specific_lane',
        ),
        migrations.RemoveField(
            model_name='location',
            name='status',
        ),
        migrations.RemoveField(
            model_name='location',
            name='view_direction',
        ),
        migrations.CreateModel(
            name='Lane',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specific_lane', models.CharField(max_length=255)),
                ('camera_id', models.CharField(max_length=255)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('lane_number', models.IntegerField()),
                ('status', models.CharField(max_length=255)),
                ('view_direction', models.IntegerField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reistijden_v1.location')),
            ],
        ),
    ]
