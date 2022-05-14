import requests
from geopy import distance
from django.conf import settings

from locations.models import Location


def fetch_coordinates(address: str):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": settings.YANDEX_APIKEY,
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
) -> float:
    order_coordinates = fetch_coordinates(order_address)
    restaurant_coordinates = fetch_coordinates(restaurant_address)
    order_distance = distance.distance(order_coordinates, restaurant_coordinates).km

    return order_distance
