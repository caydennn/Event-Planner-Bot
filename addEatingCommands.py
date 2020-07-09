from telegram.ext import ConversationHandler
import sqlfunctions as sqlf 

""" This command adds an eating place for the group """
GETPLACE = range(1)

def add_eating(update, context):
    update.message.reply_text("Add a new eating place here, or /cancel")
    return GETPLACE 

def get_place(update, context):
    group = update.effective_chat

    #* 1) Get the current group ID and group name
    group_id = str(group.id) 
    group_title = group.title
    user = update.message.from_user.username 

    #* 2) Get food place 
    food_place = update.message.text 
    context.bot.send_message (update.effective_chat.id, "Adding... ⏫⏫⏫")

    if food_place == "":
        update.message.reply_text("Please key a non empty food_place")
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
        

    context.bot.send_message (update.effective_chat.id, "{0} added {1} to food places ✅ ".format(user, food_place))
    context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))
    return ConversationHandler.END 

def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('User canceled the add eating updater. Bye {}!'.format(user.first_name))
    return ConversationHandler.END


''' DEPRECATED FUNCTION '''

def OLD_add_eating(update, context):
    group = update.effective_chat

    # 1) Get the current group ID and group name
    group_id = str(group.id) 
    group_title = group.title

    """Uncomment this during release """
    # if group_title == None:
    #     update.message.reply_text("Please key in the food place only in a group")
    #     return


    #* 2) Get the new food place and the user who sent the command
    userInput = context.args[0:]
    food_place = ' '.join(userInput)

    if food_place == "":
        update.message.reply_text("Please key in the food place after /add_eating <<Food Place>>")
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
        

    context.bot.send_message (update.effective_chat.id, "{0} added {1} to food places".format(user, food_place))
    context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))

    # return_string = '\n'.join('{}'.format(item) for item in dataDict[group_id]['food_places'])
    # context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))
