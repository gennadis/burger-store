import json

from django.http import JsonResponse
from django.templatetags.static import static


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


def register_order(request):
    order_details = json.loads(request.body.decode())

    order = Order.objects.create(
        first_name=order_details["firstname"],
        last_name=order_details["lastname"],
        phone_number=order_details["phonenumber"],
        address=order_details["address"],
    )

    for product in order_details["products"]:
        order_product = OrderProduct.objects.create(
            order=order,
            product=Product.objects.get(pk=product["product"]),
            amount=product["quantity"],
        )

    return JsonResponse({})
