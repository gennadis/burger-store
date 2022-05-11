# Generated by Django 4.0.4 on 2022-05-05 11:21

from django.db import migrations


def add_static_price(apps, schema_editor):
    OrderProduct = apps.get_model("foodcartapp", "OrderProduct")
    order_products = OrderProduct.objects.exclude(static_price__isnull=True)
    for product in order_products.iterator():
        product.static_price = product.product.price * product.amount
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ("foodcartapp", "0040_orderproduct_static_price"),
    ]

    operations = [migrations.RunPython(add_static_price)]