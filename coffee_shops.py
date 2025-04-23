import json
import requests
import folium
from geopy import distance
import os
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def get_distance(result):
    return result['distance']


def main():
    load_dotenv()
    with open("coffee.json", "r", encoding="CP1251") as coffee_shops:
        coffee_json = coffee_shops.read()
    coffee_shops = json.loads(coffee_json)

    where_are_you = input("Где Вы находитесь?")
    apikey = os.getenv('APIKEY') 
    coords1 = fetch_coordinates(apikey, where_are_you)
    results = []

    for coffee_shop in coffee_shops:
        coffee_shop_title = coffee_shop["Name"]
        coffee_shop_longitude = float(coffee_shop["Longitude_WGS84"])
        coffee_shop_latitude = float(coffee_shop["Latitude_WGS84"])
        coords2 = (coffee_shop_latitude, coffee_shop_longitude)
        coffee_shop_distance = distance.distance(coords1, coords2).km

        results.append({
            'title': coffee_shop_title,
            'distance': coffee_shop_distance,
            'latitude': coffee_shop_latitude,
            'longitude': coffee_shop_longitude
        })

    sorted_coffee_shops = sorted(results, key=get_distance)
    sorted_coffee_shops5 = sorted_coffee_shops[:5]

    m = folium.Map(location=coords1, zoom_start=12)

    for sorted_coffee_shop in sorted_coffee_shops5:
        folium.Marker(
            location=[sorted_coffee_shop['latitude'],
                      sorted_coffee_shop['longitude']],
            popup=sorted_coffee_shop['title'],
            icon=folium.Icon(color='red' if sorted_coffee_shop == sorted_coffee_shops5[0] else 'green'),
            ).add_to(m)

    m.save("index.html")


if __name__ == '__main__':
    main()
