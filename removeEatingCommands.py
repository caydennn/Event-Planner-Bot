from telegram.ext import ConversationHandler
import sqlfunctions as sqlf

""" This command removes an eating place for the group """


REMOVEPLACE = range(1)
def remove_eating(update, context):
    update.message.reply_text("Remove a eating place here, or /cancel")
    return REMOVEPLACE 

def remove_place(update, context):
    #* 1) Get the current group ID and group name
    group = update.effective_chat
    group_id = str(group.id) 
    group_title = group.title
    user = update.message.from_user.username 

    #* 2) Get food place 
    food_place = update.message.text 
    food_place = food_place.lstrip('-').lstrip()

    context.bot.send_message (update.effective_chat.id, "Loading ... ".format(food_place))

    if food_place == "":
        update.message.reply_text("Please key a non empty food_place")
        return


        
     #* 3) Update the database if the group exists, if not return an error message
    if (sqlf.check_id_exist(group_id)):

        try:
            _food_place_list = sqlf.get_group_food_data(group_id)
            if food_place.isnumeric():
                indexRemove = int(food_place) - 1
                placeRemove = _food_place_list[indexRemove]
                context.bot.send_message (update.effective_chat.id, "Removing {}... 🧹🧹🧹".format(placeRemove))
                sqlf.remove_food_data(group_id, placeRemove.upper())

            else:
                context.bot.send_message (update.effective_chat.id, "Removing {}... 🧹🧹🧹".format(food_place))

                food_place = food_place.upper()
                sqlf.remove_food_data(group_id, food_place)

            #* 4) Verify the update by sending a list of all current eating places
            food_place_list = sqlf.get_group_food_data(group_id)
            return_string = ''

            for idx in range(0 , len(food_place_list)):
                return_string += str(idx+1) + ') ' + food_place_list[idx] + '\n'
                

            context.bot.send_message (update.effective_chat.id, "{0} removed {1} from food places ✅ ".format(user, food_place))
            context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))
        except Exception as e:
            print (e)
            context.bot.send_message(update.effective_chat.id, "Error removing food place. Please check again :)")

        return ConversationHandler.END
    
def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('User canceled the remove eating place updater. Bye {}!'.format(user.first_name))
    return ConversationHandler.END


''' DEPRECATED FUNCTION '''
def OLD_remove_eating(update, context):
    group = update.effective_chat

    # 1) Get the current group ID and group name
    group_id = str(group.id) 
    group_title = group.title
    
    #* 2) Get the food place to be removed and the user who sent the command
    userInput = context.args[0:]
    food_place = ' '.join(userInput)
    if food_place == "":
        update.message.reply_text("Please key in the food place after /rm_eating <<Food Place>>")
        return
    user = update.message.from_user.username
    
    #* 3) Update the database if the group exists, if not return an error message
    if (sqlf.check_id_exist(group_id)):
        try:
            sqlf.remove_food_data(group_id, food_place)
            #* 4) Verify the update by sending a list of all current eating places
            food_place_list = sqlf.get_group_food_data(group_id)
            return_string = ''
            for idx in range(0 , len(food_place_list)):
                return_string += str(idx+1) + ') ' + food_place_list[idx] + '\n'
                

            context.bot.send_message (update.effective_chat.id, "{0} removed {1} from food places".format(user, food_place))
            context.bot.send_message (update.effective_chat.id, "The list of current food places for {0} is: \n{1}".format(group_title, return_string))
        except Exception as e:
            print (e)
            context.bot.send_message(update.effective_chat.id, "Error removing food place. Please check again :)")
