# Generated by Django 4.0.1 on 2022-03-21 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_energyuseage'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolarGeneration',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('time', models.IntegerField()),
                ('generationWh', models.FloatField()),
                ('generationKwh', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='VueEnergyUseage',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('time', models.IntegerField()),
                ('main_panel_1', models.FloatField()),
                ('main_panel_2', models.FloatField()),
                ('feed_room', models.FloatField()),
                ('south_stalls', models.FloatField()),
                ('north_stalls', models.FloatField()),
                ('garage', models.FloatField()),
                ('solar_1', models.FloatField()),
                ('solar_2', models.FloatField()),
                ('furnace', models.FloatField()),
                ('stall_lighting', models.FloatField()),
                ('rear_exterior', models.FloatField()),
                ('tack_room', models.FloatField()),
                ('stairs', models.FloatField()),
                ('water_heater', models.FloatField()),
                ('front_exterior', models.FloatField()),
                ('whirlpool', models.FloatField()),
                ('barn_bathroom', models.FloatField()),
                ('sub_panel_1', models.FloatField()),
                ('sub_panel_2', models.FloatField()),
                ('office_1', models.FloatField()),
                ('stove', models.FloatField()),
                ('microwave', models.FloatField()),
                ('bedrooms', models.FloatField()),
                ('main_half_bath', models.FloatField()),
                ('laundry', models.FloatField()),
                ('master_bathroom', models.FloatField()),
                ('kitchen_1', models.FloatField()),
                ('kitchen_2', models.FloatField()),
                ('bath_lighting', models.FloatField()),
                ('deck', models.FloatField()),
                ('living_room', models.FloatField()),
                ('refrigerator', models.FloatField()),
                ('dishwasher', models.FloatField()),
                ('office_den_kitchen', models.FloatField()),
                ('laundry_storage_pantry', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='EnergyUseage',
        ),
    ]
