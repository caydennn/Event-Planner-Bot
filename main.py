import logging
import json
import os 
from dotenv import load_dotenv

from os.path import join, dirname
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html


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

""" This command adds an eating place for the group """
def add_eating(update, context):
    group = update.effective_chat

    # 1) Get the current group ID and group name
    group_id = str(group.id) 
    group_title = group.title

    """Uncomment this during release """
    # if group_title == None:
    #     update.message.reply_text("Please key in the food place only in a group")
    #     return


    # 2) Get the new food place and the user who sent the command
    userInput = context.args[0:]
    foodPlace = ' '.join(userInput)

    if foodPlace == "":
        update.message.reply_text("Please key in the food place after /add_eating <<Food Place>>")
        return

    user = update.message.from_user.username

    # 3) Update the database if the group exists, if not create one.
    with open('data.json') as json_file:
        dataDict = json.load(json_file)

    print ("Data Dict Keys = {}".format(dataDict.keys()))
    if group_id in dataDict.keys():
        
        dataDict[group_id]['food_places'].append(foodPlace)

    else:
        # If doesnt exist, create the group 
        dataDict[group_id] = {'group_title': group_title,
                                'food_places': [foodPlace]}

    with open('data.json', 'w') as outfile:
        json.dump(dataDict, outfile)
    

    # 4) Verify the update by sending a list of all current eating places
    context.bot.send_message (update.effective_chat.id, "{0} added {1} to food places".format(user, foodPlace))
    return_string = '\n'.join('{}'.format(item) for item in dataDict[group_id]['food_places'])

    context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))




def list_eating(update, context):
    # 1) Access the database 
    with open("data.json") as json_file:
        dataDict = json.load(json_file)

    # 2) Get the current group id
    group = update.effective_chat
    group_id = str(group.id) 
    group_title = group.title

    # 2) Format and show it to the user
    return_string = '\n'.join('{}'.format(item) for item in dataDict[group_id]['food_places'])
    context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))









def main():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    TOKEN = os.environ.get("TOKEN")
    
    updater = Updater(token = TOKEN, use_context=True)
    dp = updater.dispatcher 
    dp.add_handler(CommandHandler('start', start))

    """ Test Handlers for Development """
    dp.add_handler(CommandHandler('hello', say_hello))
    dp.add_handler(CommandHandler('get_bot', get_bot))
    dp.add_handler(CommandHandler('echo', echo))

    """ Handlers """ 
    dp.add_handler(CommandHandler('add_eating', add_eating))
    dp.add_handler(CommandHandler('list_eat', list_eating))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()