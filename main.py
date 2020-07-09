import logging
import json
import os 
import sqlfunctions as sqlf 
import random 
from dotenv import load_dotenv
import addEatingCommands as AEcommands
import removeEatingCommands as REcommands 
import location as loc 

from os.path import join, dirname
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters, ConversationHandler)
from telegram.utils.helpers import mention_html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    bot_commands = context.bot.get_my_commands()
    """ Inform User about what this bot can do """
    update.message.reply_text ("These are the available commands for the bot: {}".format(bot_commands))

def say_hello(update, context):

    # User id will take the person sending out the command
    context.bot.send_message (update.effective_user.id, "This message is sent by the context using USER ID {}. Hello!".format(update.effective_user.id))
    
    # Chat id will take the group id
    context.bot.send_message (update.effective_chat.id, "This message is sent by the context using CHAT ID {}. Hello!".format(update.effective_chat.id))

    update.message.reply_text ("This message is sent by the update. Hello!")
def echo(update, context):
    # text = update.message.text 
    listCommand = context.args[0:]
    command = ' '.join(listCommand)

    update.message.reply_text("Update.message.text is {}".format(command))

def get_bot (update, context):
    context.bot.send_message(update.effective_user.id, "This is the bot {}".format(context.bot))



def list_eating(update, context):
    # 1) Get the current group id
    group = update.effective_chat
    group_id = str(group.id) 
    group_title = group.title

    # 2) Get the list of food places 
    food_place_list = sqlf.get_group_food_data(group_id)

    # 3) Format and show it to the user
    # return_string = '\n'.join('{}'.format(item) for item in food_place_list)
    return_string = ''
    for idx in range(0 , len(food_place_list)):
        return_string += str(idx+1) + ') ' + food_place_list[idx] + '\n'
        
        
    context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))

def get_eating(update, context):
    # 1) Get the current group id
    group = update.effective_chat
    group_id = str(group.id) 
    group_title = group.title

    # 2) Get the list of food places 
    food_place_list = sqlf.get_group_food_data(group_id)

    # 3) Pick a random place
    n = random.randint(0, len(food_place_list))
    picked_place = food_place_list[n] 
    print ("Picked place {}".format(picked_place))
    context.bot.send_message (update.effective_chat.id, "Maybe try {}?😋 \nIf not, type /get_eat to get another place!".format(picked_place))



def kbstart(update, context):
  update.message.reply_text(main_menu_message(),
                            reply_markup=main_menu_keyboard())

def main_menu_message():
  return 'Choose the option in main menu:'

def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Option 1', callback_data='m1')],
              [InlineKeyboardButton('Option 2', callback_data='m2')],
              [InlineKeyboardButton('Option 3', callback_data='m3')]]
  return InlineKeyboardMarkup(keyboard)



def main():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    TOKEN = os.environ.get("TOKEN")

    ''' 
    Add Eating Conversation Handler 
    '''
    add_eating_conv = ConversationHandler(
        entry_points = [CommandHandler('add_eating', AEcommands.add_eating)],
        states = {
            AEcommands.GETPLACE: [MessageHandler(Filters.regex('^(/cancel)$'), AEcommands.cancel),
                                MessageHandler(Filters.text, AEcommands.get_place) ]
        },
        fallbacks = []
    )

    '''
    Remove Eating Conversation Handler 
    '''
    remove_eating_conv = ConversationHandler(
        entry_points= [CommandHandler('rm_eating', REcommands.remove_eating)],
        states = {
            REcommands.REMOVEPLACE: [MessageHandler(Filters.regex('^(/cancel)$'), REcommands.cancel),
                                    MessageHandler(Filters.text, REcommands.remove_place)   ]
        },
        fallbacks = []
    )
    
    updater = Updater(token = TOKEN, use_context=True)
    dp = updater.dispatcher 
    dp.add_handler(CommandHandler('start', start))

    """ Test Handlers for Development """
    dp.add_handler(CommandHandler('hello', say_hello))
    dp.add_handler(CommandHandler('get_bot', get_bot))
    dp.add_handler(CommandHandler('echo', echo))
    dp.add_handler(MessageHandler(Filters.location, loc.location))
    dp.add_handler(CommandHandler('kbstart', kbstart))
    """ Handlers """ 
    # dp.add_handler(CommandHandler('add_eating', add_eating))
    dp.add_handler(CommandHandler('list_eat', list_eating))
    # dp.add_handler(CommandHandler('rm_eating', remove_eating))
    dp.add_handler(CommandHandler('get_eat', get_eating))
    dp.add_handler(add_eating_conv)
    dp.add_handler(remove_eating_conv)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()