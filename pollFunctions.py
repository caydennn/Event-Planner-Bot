from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from uuid import uuid4
import sqlfunctions as sqlf
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)

def createPoll(update: Update, context: CallbackContext):
    group = update.effective_chat
    group_id = str(group.id)

    # 1) Get the group's top places 
    food_place_list = sqlf.get_group_food_data(group_id)

    if len(food_place_list) > 1:
        # 2) Generate poll
        question = "Can't decide? Vote for your favorite few. Try to limit it to three!"
        
        context.bot.send_poll(chat_id=group_id,
        question=question, options=food_place_list,allows_multiple_answers=True, is_anonymous= False)
    else:
        context.bot.send_message("You don't have enough food places in this group! Try adding some with /add_eating")


