# Generated by Django 3.2.14 on 2022-08-16 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reistijden_v1', '0013_publication_measurement_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurementsite',
            name='first_publication_timestamp',
            field=models.DateTimeField(null=True),
        ),
    ]
