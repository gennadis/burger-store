from math import prod
from django.db import IntegrityError
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from .models import Order, OrderProduct, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse(
        [
            {
                "title": "Burger",
                "src": static("burger.jpg"),
                "text": "Tasty Burger at your door step",
            },
            {
                "title": "Spices",
                "src": static("food.jpg"),
                "text": "All Cuisines",
            },
            {
                "title": "New York",
                "src": static("tasty.jpg"),
                "text": "Food is incomplete without a tasty dessert",
            },
        ],
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


def product_list_api(request):
    products = Product.objects.select_related("category").available()

    dumped_products = []
    for product in products:
        dumped_product = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "special_status": product.special_status,
            "description": product.description,
            "category": {
                "id": product.category.id,
                "name": product.category.name,
            }
            if product.category
            else None,
            "image": product.image.url,
            "restaurant": {
                "id": product.id,
                "name": product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(
        dumped_products,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


@api_view(["POST"])
def register_order(request):
    order_details = request.data

    if (
        not all(
            isinstance(x, str)
            for x in [
                order_details.get("firstname"),
                order_details.get("lastname"),
                order_details.get("phonenumber"),
                order_details.get("address"),
            ]
        )
        or len(order_details.get("phonenumber")) == 0
    ):
        return Response(data="Bad order details!", status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.create(
            first_name=order_details["firstname"],
            last_name=order_details["lastname"],
            phone_number=order_details["phonenumber"],
            address=order_details["address"],
        )
    except (
        IntegrityError,
        KeyError,
    ):
        return Response(data="Bad order details!", status=status.HTTP_400_BAD_REQUEST)

    order_products = order_details.get("products")

    if not isinstance(order_products, list) or not order_products:
        return Response(data="Bad products!", status=status.HTTP_400_BAD_REQUEST)

    for product in order_products:
        try:
            order_product = OrderProduct.objects.create(
                order=order,
                product=Product.objects.get(pk=product["product"]),
                amount=product["quantity"],
            )
        except Product.DoesNotExist:
            return Response(
                data="Product does not exist!", status=status.HTTP_400_BAD_REQUEST
            )

    return Response(data="Order placed", status=status.HTTP_200_OK)
