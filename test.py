import os
import requests
from geopy import distance
from dotenv import load_dotenv

from foodcartapp.models import Order, Restaurant


def fetch_coordinates(apikey: str, address: str):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lat, lon


def calculate_distance(
    order_address: str,
    restaurant_address: str,
    apikey: str,
) -> float:
    order_coordinates = fetch_coordinates(apikey, order_address)
    restaurant_coordinates = fetch_coordinates(apikey, restaurant_address)
    order_distance = distance.distance(order_coordinates, restaurant_coordinates).km

    return order_distance


load_dotenv()
apikey = os.getenv("YANDEX_APIKEY")
order = Order.objects.first()
print(order.address)
rest = Restaurant.objects.last()
print(rest.address)
dist = calculate_distance(
    order_address=order.address, restaurant_address=rest.address, apikey=apikey
)
print(f"{round(dist, 2)} km.")
