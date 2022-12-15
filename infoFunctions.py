import io
import json
import os
from logging import error
from operator import itemgetter
from os.path import dirname, join
from typing import Optional, Text

import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, CallbackQuery
from telegram.ext import CallbackContext, ConversationHandler

import sqlfunctions as sqlf
import utils

# from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
# import inlinekeyboardmarkup



dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("GOOGLE_KEY")
API_KEY = os.environ.get("GOOGLE_KEY")
SE_ID = os.environ.get("SE_ID")


'''Test Function for Development'''


def test_get_location(update, context):
    print("getting location")
    print(update.message.location)


GETPLACE, CUSTOM_SEARCH_INPUT = range(2)


'''
Generates keyboard markup with group's food places so that they can choose.
Includes a Custom Search button that allows Custom Search queries when pressed.
'''
async def choose_location(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(update.effective_chat.id,  "Loading...")

    # 1. Get the list of eating places for the group
    group = update.effective_chat
    group_id = str(group.id)
    food_place_list = sqlf.get_group_food_data(group_id)
    # context.user_data['tmp_food_place_info'] = food_place_list

    # 2. Generate a button for each food list
    keyboard = []
    temp = []
    for place in food_place_list:
        temp.append(InlineKeyboardButton(place, callback_data=place))
        if len(temp) == 2:
            keyboard.append(temp)
            temp = []
        elif food_place_list[-1] == place:
            keyboard.append(temp)

    keyboard.append([InlineKeyboardButton('Custom Search', callback_data='custom_search')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Which place would you like to check? Press /cancel to stop.", reply_markup=reply_markup
    )

    return GETPLACE

'''
Handles the search operation for the choice chosen by the user from the keyboard markup
If a custom search option is chosen, it will trigger a extended conversation to ask for user input. 
'''

async def choose_location_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    food_place = query.data
    if food_place == 'custom_search':
        await query.answer("Custom Search: ")
        await query.edit_message_text("Type your custom search after a hyphen Eg. '- Mcdonalds'. Or you can /cancel your search. ")
        return CUSTOM_SEARCH_INPUT
    await query.answer(text=f"Getting Info about {food_place} ... 🌎🌍🌏")
    await search_and_send(update, context, food_place, query)
    return





async def handle_custom_search(update: Update, context: CallbackContext):
    group = update.effective_chat

    food_place = update.message.text
    food_place = food_place.lstrip('-').lstrip()
    await context.bot.send_message(update.effective_chat.id,
                             "Loading ... ".format(food_place))

    if food_place == "":
        await update.message.reply_text("Please key a non empty food_place")
        return

    await context.bot.send_message(
            update.effective_chat.id, "Getting Info about {} ... 🌎🌍🌏".format(food_place))

    await search_and_send(update, context, food_place)
    return

async def search_and_send(update: Update, context: CallbackContext, search_query: Text, initial_query: Optional[CallbackQuery] = None) -> None:
    '''
        Handles search operation and sending the results to the group

        :param update: The incoming Update object that triggered this handler
        :param context: The context in which the handler was called
        :param search_query: The search term that will be searched for using Google API
        :param initial_query (optional): Only exists when a standard option from the food place list is chosen 

        :return: The ConversationHandler.End to conclude the search operation
    '''
    try:
        results = utils.get_results(search_query)
        name, address, lat, lng, open_status, photo_reference = itemgetter(
            'name', 'address', 'lat', 'lng', 'open_status', 'photo_reference')(results)
        img = utils.get_image(photo_reference)
        if open_status:
            open_string = "Open Now ✅"
        else:
            open_string = "Closed Now 🚫"

        msgToSend = """
        {0}\n{1}\n{2}
        """.format(name, address, open_string)
        await context.bot.send_photo(update.effective_chat.id,
                               img, caption=msgToSend, parse_mode=None)
        await context.bot.send_location(
            update.effective_chat.id, latitude=lat, longitude=lng)
        if initial_query:
            await initial_query.edit_message_text(
                text=f"Info about {search_query} retrieved successfully.")
    except Exception as e:
        print(e)
        print("Error geting location of food_place")
        # context.bot.send_message(update.effective_chat.id, "Error getting info about food place. Please check again :)")
        error_text = f"Sorry, something went wrong while retrieving information about {search_query}. 😔"
        if initial_query:
            await initial_query.edit_message_text(
                text=error_text)
        else: 
            await update.message.reply_text(error_text)
        if results:
            print(results)

    return ConversationHandler.END

async def cancel(update, context):
    user = update.message.from_user
    await  update.message.reply_text('Aww okay, bye {}!'.format(user.first_name))
    return ConversationHandler.END

# print(get_results("Junction 8 Macs"))
# photoref =  "CmRaAAAAIHGi0EmQw5s2obNI77xfIvAqjCeyLTa75ugI65ocOM_MPTyEdFVAE_C0pSxxjzLFninLrtrVP-SF-OOxn7JvjPhH_VG0SncMmCZDb57G8F1PcvRCZyX9dsUa3aoiIFijEhC7_PtUzOrVEQLl835OIEw6GhQg4_DUKtd71oTS9nT9dvw-q2_B1g"
# print(get_image(photoref))
