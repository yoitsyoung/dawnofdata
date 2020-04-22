import os, telegram, telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# DEBUGGING THINGS
logger = telebot.logger
telebot.logger.setLevel(logging.CRITICAL)
mytoken = os.environ['teletoken']
bot = telebot.TeleBot(mytoken)
def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
#to receive all content types
all_content_types = ['text','document','game','audio','animation','photo','sticker','video','video_note','contact','location','venue','dice']
'''
A bot that takes user's private messages and forwards them to the group, while storing them as a list of questions to resolve. Basically a multi-pin function, where pinned messages were sent in private chats
Need to program this bot so multiple users can use at once....
Constants needed: USER_STEP and TOPIC_NAME, all should be specific to one user
'''
USER_STEP = 0
RESOLVE_STEP = 0
TOPIC_NAME = ''
topic_dict = {}
class stored_msg():
    def __init__(self, msg_id,chat_id):
        self.original_msg_id = msg_id
        self.original_chat_id = chat_id
#check if a message is a pm or a group msg
def is_msg_dm(message):
    if message.chat.type == "private":
	# private chat message
        return True
    if message.chat.type == "group":
	# group chat message
        return False
    if message.chat.type == "supergroup":
	# supergroup chat message
        return False
    if message.chat.type == "channel":
	# channel message
        return False
#I'm importing global variables in all these functions. Not sure if advisable.
#need to store message for every dtype


#this function records the text for the question
@bot.message_handler(commands=['ask'], content_types = ['text'], func=lambda message: message.chat.type == "private")
def newtopic(msg):
    global topic_dict
    global TOPIC_NAME
    global USER_STEP
    if msg.text.strip() == '/ask' :
        bot.reply_to(msg, "Try again. You didn't name a topic.")
        return
    TOPIC_NAME = msg.text.replace('/ask ','')
    topic_dict[TOPIC_NAME] = []
    #assume: there is at least a username/first_name/last_name present
    pm_chat_id = msg.chat.id
    pm_user = ''
    if msg.chat.username:
        pm_user = '@' + msg.chat.username
    elif msg.chat.first_name:
        pm_user = msg.chat.first_name
    elif msg.chat.last_name:
        pm_user = msg.chat.last_name
    else:
        pm_user = 'User Unknown'
    bot.reply_to(msg, "Your messages are now being recorded!")
    USER_STEP = 1
@bot.message_handler(content_types = all_content_types, func=lambda message: USER_STEP == 1 and message.text != '/end')
def storemsg_text(msg):
    newitem = stored_msg(msg.message_id, msg.chat.id)
    print(msg.message_id)
    #dump(msg)
    global topic_dict
    global TOPIC_NAME
    if TOPIC_NAME not in topic_dict:
        topic_dict[TOPIC_NAME] = []
    topic_dict[TOPIC_NAME].append(newitem)
    print(topic_dict)
    
@bot.message_handler(commands = ['end'])
def end_text(msg):
    global USER_STEP
    global TOPIC_NAME
    bot.reply_to(msg, "Recording has ended. Do not delete this chat, or my memory will be wiped!")
    USER_STEP = 0
    TOPIC_NAME = ''

#this function gets the list of questions, while sending a message indicating the question topic and corresponding number
@bot.message_handler(commands=['questions'])
def gen_keyboard(msg):
    global topic_dict
    global TOPIC_NAME
    global USER_STEP
    print(topic_dict)
    markup = ReplyKeyboardMarkup()
    question_text = \
    '''
    Right away. Here are this list of questions. Tap the corresponding number to find out more: \n
    '''
    for number, topic in enumerate(topic_dict.keys()):
        number += 1
        question_text += str(number) + '. ' + str(topic) + '\n'
        markup.add(InlineKeyboardButton(str(number)))            
    print(question_text)               
    bot.send_message(chat_id = msg.chat.id, text = question_text, reply_markup=markup)
    USER_STEP = 2


@bot.message_handler(func=lambda message: USER_STEP == 2)
def forward_message(selected_msg):
    global topic_dict
    global TOPIC_NAME
    global USER_STEP
    
    try:
        current_chat_id = selected_msg.chat.id
        index = int(selected_msg.text) - 1
        selected_topic = list(topic_dict.keys())[index]
        #get corresponding topic value from number.... not advised, should fix. But after Py3.7, dictionaries maintain orders by default
        for message in topic_dict[selected_topic]:
            bot.forward_message(chat_id = current_chat_id , from_chat_id = message.original_chat_id , message_id = message.original_msg_id)
        bot.send_message(chat_id = selected_msg.chat.id, text = '**----End of Question----**', reply_markup = ReplyKeyboardRemove())
        USER_STEP = 0
    except KeyError as e:
        bot.send_message(chat_id = selected_msg.chat.id, text = 'Please key in a valid number! Try again.', reply_markup = ReplyKeyboardRemove())
    except ValueError as v:
        bot.send_message(chat_id = selected_msg.chat.id, text = 'Please key in a number not text! Try again.', reply_markup = ReplyKeyboardRemove())

#Now, a function to resolve a question
@bot.message_handler(commands=['resolve'], content_types = ['text'], func=lambda message: message.chat.type == "private")
def killtopic(msg):
    global topic_dict
    
    global RESOLVE_STEP
    print(topic_dict)
    markup = ReplyKeyboardMarkup()
    resolve_text = \
    '''
    Right away. Which question would you like to resolve?: \n
    '''
    try:
        for number, topic in enumerate(topic_dict.keys()):
            number += 1
            resolve_text += str(number) + '. ' + str(topic) + '\n'
            markup.add(InlineKeyboardButton(str(number)))            
        print(resolve_text)               
        bot.send_message(chat_id = msg.chat.id, text = resolve_text, reply_markup=markup)
        RESOLVE_STEP = 1
    except KeyError as e:
        bot.send_message(chat_id = msg.chat.id, text = 'Please key in a valid number! Try again.', reply_markup = ReplyKeyboardRemove())
        print(e)
    except ValueError as v:
        bot.send_message(chat_id = msg.chat.id, text = 'Please key in a number not text! Try again.', reply_markup = ReplyKeyboardRemove())
        print(v)
@bot.message_handler(func=lambda message: RESOLVE_STEP == 1)
def check_user_del_topic(msg):
    global topic_dict
    global RESOLVE_STEP
    current_chat_id = msg.chat.id
    index = int(msg.text) - 1
    selected_topic = list(topic_dict.keys())[index]
    stored_chat_id = topic_dict[selected_topic][0].original_chat_id
    if stored_chat_id != current_chat_id:
        bot.send_message(chat_id = current_chat_id, text = 'You\'re not the user who posted the question!')
    else:
        removed_value = topic_dict.pop(selected_topic, 'ERROR: No Key found') 
        bot.send_message(chat_id = current_chat_id, text = 'Question removed! Thank the user who answered you.', reply_markup = ReplyKeyboardRemove())
    RESOLVE_STEP = 0

bot.polling()