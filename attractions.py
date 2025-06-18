import googlemaps
from discord.ext import commands
import polyline
from geopy import distance
import pandas as pd
import os

gmaps_key = os.environ.get('GMAPS_KEY')

gmaps = googlemaps.Client(key=gmaps_key)

def check_address(address):
    address_val = gmaps.addressvalidation(address, regionCode='PL')

    verdict = address_val['result']['verdict']
    city = address_val['result']['address']['postalAddress']['locality'].lower()

    if verdict.get('hasUnconfirmedComponents'):
        raise commands.CommandError(f'Address is not confirmed. Remember to write address in "" e.g. "plac Defilad 1 Warszawa"')

    # if city != 'warszawa':
    #     raise commands.CommandError(f'Only addresses in Warsaw are allowed')

    lat = address_val['result']['geocode']['location']['latitude']
    long = address_val['result']['geocode']['location']['longitude']

    return (lat, long)

def check_travel_mode(mode):
    travel_modes = ['driving', 'walking', 'bicycling', 'transit']

    if mode not in travel_modes:
        raise commands.CommandError(f'Not recognized travel mode. Remember to choose travel mode from: driving, walking, bicycling, transit')

    return mode


def find_attractions(latlong_origin, latlong_dest, num, travel_mode):
    route = gmaps.directions(latlong_origin, latlong_dest, mode=travel_mode)
    overview_polyline = route[0]["overview_polyline"]["points"]
    overview_polyline = polyline.decode(overview_polyline)

    places_data = {'Name': [], 'Id': [], 'Lat': [], 'Long': [], 'Rating': [], 'User_rating': []}
    found_places = set()

    for _, point in enumerate(overview_polyline):

        radius = 500

        places = gmaps.places(query='attraction', location=point, radius=radius)

        for i, data in enumerate(places['results']):
            place_id = data['place_id']
            if place_id in found_places:
                continue

            lat = data['geometry']['location']['lat']
            lng = data['geometry']['location']['lng']
            real_distance = distance.distance(point, (lat, lng)).meters
            if real_distance > radius:
                continue

            found_places.add(place_id)

            name = data['name']
            rating = data.get('rating', 0)
            user_rating_total = data.get('user_ratings_total', 0)

            places_data['Name'].append(name)
            places_data['Id'].append(place_id)
            places_data['Lat'].append(lat)
            places_data['Long'].append(lng)
            places_data['Rating'].append(rating)
            places_data['User_rating'].append(user_rating_total)

    df = pd.DataFrame(places_data)

    df_sorted = df.sort_values(by=['Rating', 'User_rating'], ascending=False).head(num)

    attractions_latlong = list(zip(df_sorted['Lat'], df_sorted['Long']))
    names = list(df_sorted['Name'])

    optimize_route = gmaps.directions(latlong_origin, latlong_dest, mode=travel_mode, waypoints=attractions_latlong,
                                      optimize_waypoints=True)
    order = optimize_route[0]['waypoint_order']

    optimized_attractions = [attractions_latlong[i] for i in order]
    optimized_names = [names[i] for i in order]

    return optimized_attractions, optimized_names


def create_url(latlong_origin, latlong_dest, attractions, travel_mode):

    url = "https://www.google.com/maps/dir/?api=1"
    origin = "&origin=" + str(latlong_origin[0]) + "," + str(latlong_origin[1])
    dest = "&destination=" + str(latlong_dest[0]) + "," + str(latlong_dest[1])
    choosen_travel_mode = "&travelmode=" + travel_mode

    if attractions:
        waypoints = "&waypoints=" + "|".join([f"{lat},{lng}" for lat, lng in attractions])
    else:
        waypoints = ""

    return url + origin + dest + waypoints + choosen_travel_mode