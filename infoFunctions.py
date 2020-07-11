import sqlfunctions as sqlf 
import os
import requests, json 
import io 

from telegram.ext import ConversationHandler
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("GOOGLE_KEY")
SE_ID = os.environ.get("SE_ID")


'''Test Function for Development'''

def test_get_location(update, context):
    print ("getting location")
    print(update.message.location)

GETPLACE = range(1)

def choose_location(update, context):
    update.message.reply_text("Get the information about the eating place, or /cancel")
    return GETPLACE



def get_results(food_place):
    '''
    # Results contain the following information:
    'formatted_address'
    'geometry':{'location':{'lat': ... , 'lng':}}
    'name'
    'opening_hours': {'open_now': True}
    '''
    query = food_place 
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    r = requests.get(url + 'query=' + query +
                        '&key=' + API_KEY) 
    x = r.json() 
    results = x['results'][0]
    return results 


def get_image(photoref):
    maxwidth= "400"

    url = "https://maps.googleapis.com/maps/api/place/photo?"
    r = requests.get(url + 'maxwidth=' + maxwidth +
                    '&photoreference=' + photoref
                    +'&key=' + API_KEY)

    return io.BytesIO(r.content) 

def get_place_location(update, context ):
    #* 1) Get the current group ID and group name
    group = update.effective_chat
    group_id = str(group.id) 
    group_title = group.title
    user = update.message.from_user.username 

    food_place = update.message.text 
    food_place = food_place.lstrip('-').lstrip()

    context.bot.send_message (update.effective_chat.id, "Getting Info about {} ... 🌎🌍🌏".format(food_place))
    if food_place == "":
        update.message.reply_text("Please key a non empty food_place")
        return

    #* 2) If group exists, get the index of the place
    try: 
        # Get the current list of food places for the group 
        _food_place_list = sqlf.get_group_food_data(group_id)
        if food_place.isnumeric():
            indexFind = int(food_place) - 1
            placeToFind = _food_place_list[indexFind]
            results = get_results(placeToFind)
            

        else:
            results = get_results(food_place)
            
        name = results['name']
        address = results['formatted_address']
        coordinates = results['geometry']['location']
        lat = coordinates['lat']
        lng = coordinates['lng']
        open_status = results['opening_hours']['open_now']

        photo_reference = results['photos'][0]['photo_reference']
        img = get_image(photo_reference)

        if open_status:
            open_string = "Open Now ✅"
        else:
            open_string = "Closed Now 🚫"
        
        msgToSend = """
        {0}\n{1}\n{2}
        """.format(name, address, open_string)
        # context.bot.send_message(update.effective_chat.id, msgToSend)
        context.bot.send_photo(update.effective_chat.id, img, caption=msgToSend, parse_mode=None)
        context.bot.send_location(update.effective_chat.id, latitude=lat, longitude=lng)

    except Exception as e:
        print (e)
        if results:
            print(results)
        print ("Error geting location of food_place")


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('User canceled the operation. Bye {}!'.format(user.first_name))
    return ConversationHandler.END
    
# print(get_results("Junction 8 Macs"))
# photoref =  "CmRaAAAAIHGi0EmQw5s2obNI77xfIvAqjCeyLTa75ugI65ocOM_MPTyEdFVAE_C0pSxxjzLFninLrtrVP-SF-OOxn7JvjPhH_VG0SncMmCZDb57G8F1PcvRCZyX9dsUa3aoiIFijEhC7_PtUzOrVEQLl835OIEw6GhQg4_DUKtd71oTS9nT9dvw-q2_B1g"
# print(get_image(photoref))
