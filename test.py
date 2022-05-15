from foodcartapp.models import Restaurant
from locations.models import Location
from locations.geocoding import fetch_coordinates


def add_restaurants_locations():
    for restaurant in Restaurant.objects.all():
        latitude, longitude = fetch_coordinates(restaurant.address)
        restaurant_location = Location.objects.get_or_create(
            address=restaurant.address,
            latitude=latitude,
            longitude=longitude,
        )
        print(restaurant_location)


add_restaurants_locations()
