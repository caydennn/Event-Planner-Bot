import asyncio
import json
import logging
import os
import random
from dataclasses import dataclass
from os.path import dirname, join

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (Application, CallbackContext, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          ExtBot, MessageHandler, PollAnswerHandler,
                          PollHandler, Updater, filters)

import addEatingCommands as AEcommands
import infoFunctions as infof
import pollFunctions as pollf
import removeEatingCommands as REcommands
import sqlfunctions as sqlf

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update, context):
    logger.info("Received start command from {} , {}".format(update.effective_user.id, update.effective_user.username))
    bot_commands = await context.bot.get_my_commands()
    """ Inform User about what this bot can do """
    await  update.message.reply_text(
        "These are the available commands for the bot: {}".format(bot_commands))


async def say_hello(update, context):

    # User id will take the person sending out the command
    await context.bot.send_message(
        update.effective_user.id, "This message is sent by the context using USER ID {}. Hello!".format(update.effective_user.id))

    # Chat id will take the group id
    await context.bot.send_message(
        update.effective_chat.id, "This message is sent by the context using CHAT ID {}. Hello!".format(update.effective_chat.id))

    await update.message.reply_text("This message is sent by the update. Hello!")


async def echo(update, context):
    # text = update.message.text
    listCommand = context.args[0:]
    command = ' '.join(listCommand)

    await update.message.reply_text("Update.message.text is {}".format(command))


async def get_bot(update, context):
    await context.bot.send_message(update.effective_user.id,
                             "This is the bot {}".format(await context.bot))


async def help(update: Update, context: CallbackContext):
    help_text = """
*Welcome to Event Planner Bot*
Hey there! I can help you plan your outings with your social groups by keeping track of your favorite eating places!

*What can I do?*
/add_eating - Add a new favorite place to the list
/rm_eating - Remove an existing place from the list 
/get_info - Get information such as address, opening hours, directions to any place!
/list_eat - View the list of places for the group
/get_eat - Suggest a random eating place for the group 
/create_poll - Create a poll from your groups Top 10 Eating Places! 
/help - View this help message if you ever forget what I can do ☺️ 
    """
    logger.info("Received help command from {} , {}".format(update.effective_user.id, update.effective_user.username))
    help_text = help_text.replace("!" , "\\!").replace("-", "\\-").replace("_", "\\_")

    await context.bot.send_message(update.effective_chat.id , help_text, parse_mode =  ParseMode.MARKDOWN_V2)
    await context.bot.send_message(
        update.effective_chat.id, "Get help planning outings! Always add a dash ('-') before replying to the bot 😊")


async def list_eating(update, context):
    # 1) Get the current group id
    group = update.effective_chat
    group_id = str(group.id)
    group_title = group.title

    # 2) Get the list of food places
    food_place_list = sqlf.get_group_food_data(group_id)

    # 3) Format and show it to the user
    # return_string = '\n'.join('{}'.format(item) for item in food_place_list)
    return_string = ''
    for idx in range(0, len(food_place_list)):
        return_string += str(idx+1) + ') ' + food_place_list[idx] + '\n'

    await context.bot.send_message(update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(
        group_title, return_string))


async def get_random_eating(update, context):
    # 1) Get the current group id
    group = update.effective_chat
    group_id = str(group.id)
    group_title = group.title

    # 2) Get the list of food places
    food_place_list = sqlf.get_group_food_data(group_id)

    # 3) Pick a random place
    n = random.randint(0, len(food_place_list))
    picked_place = food_place_list[n]
    print("Picked place {}".format(picked_place))
    await context.bot.send_message(
        update.effective_chat.id, "Maybe try {}?😋 \nIf not, type /get_eat to get another place!".format(picked_place))


async def kbstart(update, context):
    await update.message.reply_text(main_menu_message(),
                              reply_markup=main_menu_keyboard())


def main_menu_message():
    return 'Choose the option in main menu:'


def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Option 1', callback_data='m1')],
                [InlineKeyboardButton('Option 2', callback_data='m2')],
                [InlineKeyboardButton('Option 3', callback_data='m3')]]
    return InlineKeyboardMarkup(keyboard)




@dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""

    user_id: int
    payload: str


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)

async def main() -> None:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    TOKEN = os.environ.get("TOKEN")
    app = FastAPI()
    
   
    
    
    
    print ("TOKEN is {}".format(TOKEN))
    ''' 
    Add Eating Conversation Handler 
    '''
    add_eating_conv = ConversationHandler(
        entry_points=[CommandHandler('add_eating', AEcommands.add_eating)],
        states={
            AEcommands.GETPLACE: [MessageHandler(filters.Regex('^(/cancel|/cancel@event_planner_bot)$'), AEcommands.cancel),
                                  MessageHandler(filters.Regex('^-'), AEcommands.get_place)]
        },
        fallbacks=[]
    )

    '''UPDATED Remove Eating Handler'''
    remove_eating_conv = ConversationHandler(
        entry_points=[CommandHandler(
            'rm_eating', REcommands.remove_eating_place)],
        states={
            REcommands.REMOVEPLACE: [MessageHandler(filters.Regex('^(/cancel|/cancel@event_planner_bot)$'), REcommands.cancel),
                                     CallbackQueryHandler(REcommands.remove_eating_callback)]
        },
        fallbacks=[]
    )

    get_location_conv = ConversationHandler(
        entry_points=[CommandHandler(
            'get_info', infof.choose_location)],  # ! check this
        states={infof.GETPLACE: [MessageHandler(filters.Regex('^(/cancel|/cancel@event_planner_bot)$'), infof.cancel),
                                 CallbackQueryHandler(
                                     infof.choose_location_callback)
                                 #
                                 ],
                infof.CUSTOM_SEARCH_INPUT: [MessageHandler(filters.Regex('^(/cancel|/cancel@event_planner_bot)$'), infof.cancel),
                                            MessageHandler(filters.Regex('^-+'), infof.handle_custom_search)]

                },

        fallbacks=[]
    )

    '''
    Get Info Conversation Handler
    '''
   

    # updater = Updater(token=TOKEN, use_context=True)
    # logger.info(updater.bot.get_me())
    # dp = updater.dispatcher
    # dp.add_handler(CommandHandler('start', start))
    context_types = ContextTypes(context=CustomContext)
    dp = Application.builder().token(TOKEN).updater(None).context_types(context_types).build() #todo: rename this to app

    """ Test Handlers for Development """
    # dp.add_handler(CommandHandler('hello', say_hello))
    # dp.add_handler(CommandHandler('get_bot', get_bot))
    # dp.add_handler(CommandHandler('echo', echo))
    # dp.add_handler(MessageHandler(Filters.location, infof.test_get_location))
    # dp.add_handler(CommandHandler('kbstart', kbstart))


    """ Handlers """
    # dp.add_handler(CommandHandler('add_eating', add_eating))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('list_eat', list_eating))
    dp.add_handler(CommandHandler('get_eat', get_random_eating))
    dp.add_handler(CommandHandler('create_poll', pollf.createPoll))
    
    dp.add_handler(add_eating_conv)
    dp.add_handler(remove_eating_conv)
    dp.add_handler(get_location_conv)
    
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    if WEBHOOK_URL is None:
        return Exception ("WEBHOOK_URL is not set")
    # Pass webhook settings to telegram
    await dp.bot.set_webhook(url=f"{WEBHOOK_URL}/telegram")


    @app.post("/telegram")
    async def telegram(request: Request) -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await dp.update_queue.put(
            Update.de_json(data=await request.json(), bot=dp.bot)
        )
        return Response()
    
    @app.get('/')
    async def root():
        return {'message': 'Hello World'}
    webserver = uvicorn.Server(config = uvicorn.Config(app, host = '0.0.0.0', port = 8080))
    
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        logging.error(f"{request}: {exc_str}")
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    async with dp:

        await dp.start()

        await webserver.serve()
        await dp.stop()
    
    # updater.start_polling()
    # updater.idle()


if __name__ == "__main__":
    asyncio.run(main())
