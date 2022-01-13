from typing import List, Optional
import requests 
import io
import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
GOOGLE_API_KEY = os.environ.get("GOOGLE_KEY")

def format_list(food_place_list: List, group_title: Optional[str] = 'this group'):
    food_place_list_str = ''
    for idx in range(0, len(food_place_list)):
        food_place_list_str += str(idx+1) + '\) ' + food_place_list[idx] + '\n'

    return_string = "The list of current food places for {0} is: \n{1}".format(
        group_title, food_place_list_str)
    return return_string


def parse_search_results(results):
    name = results['name']
    address = results['formatted_address']
    coordinates = results['geometry']['location']
    lat = coordinates['lat']
    lng = coordinates['lng']
    open_status = results['opening_hours']['open_now']
    photo_reference = results['photos'][0]['photo_reference']
    ret = {
        'name': name,
        'address': address,
        'lat': lat,
        'lng': lng,
        'open_status': open_status,
        'photo_reference': photo_reference
    }
    return ret 

def get_image(photoref):
    maxwidth= "400"

    url = "https://maps.googleapis.com/maps/api/place/photo?"
    r = requests.get(url + 'maxwidth=' + maxwidth +
                    '&photoreference=' + photoref
                    +'&key=' + GOOGLE_API_KEY)

    return io.BytesIO(r.content) 


def get_results(food_place):
    '''
    ### Results contain the following information:
    - 'formatted_address' \n
    - 'geometry':{'location':{'lat': ... , 'lng':}} \n
    - 'name' \n
    - 'opening_hours': {'open_now': True}
    '''
    query = 'Singapore ' + food_place
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    r = requests.get(url + 'query=' + query +
                     '&key=' + GOOGLE_API_KEY)
    x = r.json()
    results = x['results'][0]
    return parse_search_results(results)
