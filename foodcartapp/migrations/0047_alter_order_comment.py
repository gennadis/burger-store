# Generated by Django 4.0.4 on 2022-05-17 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_order_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, max_length=500, verbose_name='комментарий'),
        ),
    ]