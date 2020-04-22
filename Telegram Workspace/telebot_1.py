
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging, os, datetime
mytoken = os.environ['teletoken']
print('Your token is: ' + mytoken)
print('We shall proceed')
admin_id = 242546822
group_id = 1001358411804


from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import telegram

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
bot = telegram.Bot(mytoken)
GET_IMG = range(1)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def forwardmsg(update, context):
    current_id = update.message.chat_id
    #new_id = 
def logmsg(update, context):
    sender_name = update.message.from_user.username
    msgtext = update.message.text
    unixtime = update.message.date
    datestr = unixtime.strftime("%d-%m-%Y %H-%M-%S")
    fulltext = 'At date ' + datestr + ', ' + sender_name + ' sent this message: ' + '\n' + msgtext
    bot.send_message(chat_id = admin_id, text = fulltext)

def newstart(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!! This chat id is: ' + str(update.effective_chat.id))

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def send_ask_advice(update, context):
        update.message.reply_text('Send your question and picture separately! Do NOT send your photo as a file, the bot will not register')
        return GET_IMG


def get_img(update, context):
    print(update.message)
    telegram_file_id = update.message.photo[-1].file_id
    print(telegram_file_id)
    sender_name = "@"
    if update.message.from_user.username != None:
        sender_name += update.message.from_user.username
    response = 'Now, ' + sender_name + ' sent in a photo of file_id ' + telegram_file_id
    bot.send_photo(chat_id = admin_id, photo = telegram_file_id)
    bot.send_message(chat_id = admin_id, text = response)
    bot.send_photo(chat_id = group_id, photo = telegram_file_id)
    return GET_IMG

def get_text(update, context):
    sender_name = "@"
    sender_name += update.message.from_user.username
    msgtext = update.message.text
    unixtime = update.message.date
    datestr = unixtime.strftime("%d-%m-%Y %H-%M-%S")
    fulltext = 'At date ' + datestr + ', ' + sender_name + ' sent this message: ' + '\n' + msgtext
    bot.send_message(chat_id = admin_id, text = fulltext)
    bot.send_message(chat_id = group_id, text = msgtext)
    return GET_IMG







ask_handler = ConversationHandler(
        entry_points=[CommandHandler('ask', send_ask_advice)],

        states={
            GET_IMG: [MessageHandler(Filters.photo, get_img),
                      MessageHandler(Filters.text, get_text)]

        },
        fallbacks=[MessageHandler(Filters.document, send_ask_advice),
                   CommandHandler('ask', send_ask_advice)]
    )


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token = mytoken, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", newstart))
    dp.add_handler(ask_handler)

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    


if __name__ == '__main__':
    main()