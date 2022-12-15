import json  # for printing

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      Update)
from telegram.ext import CallbackContext, ConversationHandler
from telegram.constants import ParseMode
import sqlfunctions as sqlf
import utils

""" This command removes an eating place for the group """

REMOVEPLACE = range(1)


async def cancel(update, context):
    user = update.message.from_user
    await update.message.reply_text(
        'User canceled the remove eating place updater. Bye {}!'.format(user.first_name))
    return ConversationHandler.END


"""
Remove Eating Command
- Uses inline keyboard for selection
"""


async def remove_eating_place(update: Update, context: CallbackContext) -> None:

    await context.bot.send_message(update.effective_chat.id,  "Loading...")
    # 1. Get the list of eating places for the group
    group = update.effective_chat
    group_id = str(group.id)
    food_place_list = sqlf.get_group_food_data(group_id)

    print(food_place_list)
    print(context.user_data)
    context.user_data['tmp_food_place_rm'] = food_place_list

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

    # keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel_rm')])
    # print("Keyboard: ")

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Please choose which place to remove, or press /cancel to stop:', reply_markup=reply_markup)
    return REMOVEPLACE


async def remove_eating_callback(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # print("Query")
    # print(query.to_json())

    await query.answer(text=f"Removing {query.data}... 🧹🧹🧹")
    group = update.effective_chat
    group_id = str(group.id)
    print(f"Deleting {query.data}...")
    sqlf.remove_food_data(group_id, query.data)
    print("User Data")
    print(context.user_data)
    # Provide verification to user
    tmp_food_place_list = context.user_data.get('tmp_food_place_rm', None)
    if tmp_food_place_list:
        tmp_food_place_list.remove(query.data)
        group_title = group.title
        verification = utils.format_list(
            food_place_list=tmp_food_place_list, group_title=group_title)
        await query.edit_message_text(
            text=f"Deleted: *{query.data}*\n\n{verification}", parse_mode=ParseMode.MARKDOWN_V2)
    else: 
        await query.edit_message_text(
            text=f"Deleted: *{query.data}* successfully", parse_mode=ParseMode.MARKDOWN_V2)
        

    return ConversationHandler.END

''' DEPRECATED FUNCTIONS BELOW '''
async def old_remove(update, context):
    # * 1) Get the current group ID and group name
    group = update.effective_chat
    group_id = str(group.id)
    group_title = group.title
    user = update.message.from_user.username

    # * 2) Get food place
    food_place = update.message.text
    food_place = food_place.lstrip('-').lstrip()

    await context.bot.send_message(update.effective_chat.id,
                             "Loading ... ".format(food_place))

    if food_place == "":
        await update.message.reply_text("Please key a non empty food_place")
        return

     # * 3) Update the database if the group exists, if not return an error message
    if (sqlf.check_id_exist(group_id)):

        try:
            _food_place_list = sqlf.get_group_food_data(group_id)
            if food_place.isnumeric():
                indexRemove = int(food_place) - 1
                placeRemove = _food_place_list[indexRemove]
                await context.bot.send_message(
                    update.effective_chat.id, "Removing {}... 🧹🧹🧹".format(placeRemove))
                sqlf.remove_food_data(group_id, placeRemove.upper())

            else:
                await context.bot.send_message(
                    update.effective_chat.id, "Removing {}... 🧹🧹🧹".format(food_place))

                food_place = food_place.upper()
                sqlf.remove_food_data(group_id, food_place)

            # * 4) Verify the update by sending a list of all current eating places
            food_place_list = sqlf.get_group_food_data(group_id)
            return_string = ''

            for idx in range(0, len(food_place_list)):
                return_string += str(idx+1) + ') ' + \
                    food_place_list[idx] + '\n'

            await context.bot.send_message(
                update.effective_chat.id, "{0} removed {1} from food places ✅ ".format(user, food_place))
            await context.bot.send_message(update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(
                group_title, return_string))
        except Exception as e:
            print(e)
            await context.bot.send_message(
                update.effective_chat.id, "Error removing food place. Please check again :)")

        return ConversationHandler.END
