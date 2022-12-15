from telegram.ext import ConversationHandler
from telegram.ext import CallbackContext
from telegram import  Update

import sqlfunctions as sqlf 

""" This command adds an eating place for the group """
GETPLACE = range(1)

async def add_eating(update: Update, context: CallbackContext):
    await update.message.reply_text("Add a new eating place to your group here by typing it after a hyphen Eg. '- McDonalds' , or press /cancel to stop.")
    return GETPLACE 

async def get_place(update, context):
    group = update.effective_chat

    #* 1) Get the current group ID and group name
    group_id = str(group.id) 
    group_title = group.title
    user = update.message.from_user.username 

    #* 2) Get food place 
    food_place = update.message.text 
    food_place = food_place.lstrip('-').lstrip()

    await context.bot.send_message (update.effective_chat.id, "Adding {}... ⏫⏫⏫".format(food_place))

    if food_place == "":
        await update.message.reply_text("Please key a non empty food_place")
        return

    #* 3) Update the database if the group exists, if not create one.
    if (sqlf.check_id_exist(group_id)):
        # Update the food database
        sqlf.insert_food_data(group_id, food_place)

    else:
        sqlf.insert_group_data(group_id, group_title)
        sqlf.insert_food_data(group_id, food_place)
        
   #* 4) Verify the update by sending a list of all current eating places
    food_place_list = sqlf.get_group_food_data(group_id)
    return_string = ''
    for idx in range(0 , len(food_place_list)):
        return_string += str(idx+1) + ') ' + food_place_list[idx] + '\n'
        

    await context.bot.send_message (update.effective_chat.id, "{0} added {1} to food places ✅ ".format(user, food_place))
    await context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))
    return ConversationHandler.END 

async def cancel(update, context):
    user = update.message.from_user
    await update.message.reply_text('User canceled the add eating updater. Bye {}!'.format(user.first_name))
    return ConversationHandler.END


''' 
# DEPRECATED FUNCTION 
This function used to take the arguments following the /add_eating command 
This is no longer used.

'''

async def OLD_add_eating(update, context):
    group = update.effective_chat

    # 1) Get the current group ID and group name
    group_id = str(group.id) 
    group_title = group.title

    """Uncomment this during release """
    # if group_title == None:
    #     await update.message.reply_text("Please key in the food place only in a group")
    #     return


    #* 2) Get the new food place and the user who sent the command
    userInput = context.args[0:]
    food_place = ' '.join(userInput)

    if food_place == "":
        await update.message.reply_text("Please key in the food place after /add_eating <<Food Place>>")
        return

    user = update.message.from_user.username

    #* 3) Update the database if the group exists, if not create one.
    if (sqlf.check_id_exist(group_id)):
        # Update the food database
        sqlf.insert_food_data(group_id, food_place)

    else:
        sqlf.insert_group_data(group_id, group_title)
        sqlf.insert_food_data(group_id, food_place)


    #* 4) Verify the update by sending a list of all current eating places
    food_place_list = sqlf.get_group_food_data(group_id)
    return_string = ''
    for idx in range(0 , len(food_place_list)):
        return_string += str(idx+1) + ') ' + food_place_list[idx] + '\n'
        

    await context.bot.send_message (update.effective_chat.id, "{0} added {1} to food places".format(user, food_place))
    await context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))

    # return_string = '\n'.join('{}'.format(item) for item in dataDict[group_id]['food_places'])
    # await context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))
