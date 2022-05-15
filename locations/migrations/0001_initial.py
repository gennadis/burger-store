# Generated by Django 4.0.4 on 2022-05-14 17:54

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200, unique=True, verbose_name='адрес')),
                ('latitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)], verbose_name='широта')),
                ('longitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)], verbose_name='долгота')),
                ('requested_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='запрос координат осуществлен')),
            ],
            options={
                'verbose_name': 'локация',
                'verbose_name_plural': 'локации',
            },
        ),
    ]