# Generated by Django 4.0.1 on 2022-03-30 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_energyuse_delete_vueenergyuseage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energyuse',
            name='time',
            field=models.TimeField(),
        ),
    ]