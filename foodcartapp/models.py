from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from locations import geocoding
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField(
        "адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(availability=True).values_list(
            "product"
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="категория",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        "цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField(
        "описание",
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="продукт",
    )
    availability = models.BooleanField("в продаже", default=True, db_index=True)

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [["restaurant", "product"]]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_total_prices(self):
        return self.annotate(total_price=Sum("products__static_price"))

    def with_restaurants(self):
        for order in self:
            order_products = order.order_products.values("product")
            restaurant_products = (
                RestaurantMenuItem.objects.select_related("restaurant", "product")
                .filter(availability=True)
                .filter(product__in=order_products)
            )

            products = set(position.product for position in restaurant_products)

            restaurants = []
            for product in products:
                restaurants_with_product = set(
                    position.restaurant
                    for position in restaurant_products
                    if position.product == product
                )
                restaurants.append(restaurants_with_product)

            suitable_restaurants = restaurants[0].intersection(*restaurants)

            suitable_restaurants_with_distances = []
            for restaurant in suitable_restaurants:
                distance = geocoding.calculate_distance(
                    order_address=order.address,
                    restaurant_address=restaurant.address,
                )
                suitable_restaurants_with_distances.append((restaurant, distance))

            order.suitable_restaurants_with_distances = sorted(
                suitable_restaurants_with_distances, key=lambda pair: pair[1]
            )

        return self


class Order(models.Model):
    # Order status choices
    NEW = 0
    CONFIRMED = 1
    COOKING = 2
    DELIVERY = 3
    FINISHED = 4
    STATUS_CHOICES = [
        (NEW, "Новый"),
        (CONFIRMED, "Подтвержден"),
        (COOKING, "Готовка"),
        (DELIVERY, "Доставка"),
        (FINISHED, "Выполнен"),
    ]

    # Payment choices
    CREDIT_CARD = 0
    CASH = 1
    PAYMENT_CHOICES = [
        (CREDIT_CARD, "карта"),
        (CASH, "наличные"),
    ]

    first_name = models.CharField(
        verbose_name="имя",
        max_length=20,
    )
    last_name = models.CharField(
        verbose_name="фамилия",
        max_length=40,
    )
    phone_number = PhoneNumberField(
        verbose_name="номер телефона",
        db_index=True,
    )
    address = models.CharField(
        verbose_name="адрес доставки",
        max_length=100,
        validators=[MinLengthValidator(10)],
    )
    comment = models.TextField(
        verbose_name="комментарий",
        max_length=500,
        blank=True,
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=NEW,
        db_index=True,
    )
    payment = models.PositiveSmallIntegerField(
        choices=PAYMENT_CHOICES,
        db_index=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name="готовит",
        related_name="orders",
        null=True,
        blank=True,
    )
    registered_at = models.DateTimeField(
        verbose_name="оформлен",
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        verbose_name="подтвержден",
        db_index=True,
        blank=True,
        null=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name="доставлен",
        db_index=True,
        blank=True,
        null=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

    def __str__(self):
        return f"{self.first_name}, {self.address}"


class OrderProduct(models.Model):
    order = models.ForeignKey(
        to=Order,
        verbose_name="состав заказа",
        related_name="order_products",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        to=Product,
        verbose_name="продукт",
        related_name="order_products",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="количество",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    static_price = models.DecimalField(
        verbose_name="Фиксированная стоимость",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "позиция заказа"
        verbose_name_plural = "позиции заказа"

    def __str__(self):
        return f"{self.product} - {self.amount}"
