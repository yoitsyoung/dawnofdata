def send_ask_advice(bot, update):
        update.message.reply_text('Send your question and picture separately!')
        return GET_IMG


def get_img(bot, update):
    print(update.message)
    telegram_file_id = update.message.photo[-1].file_id
    print(telegram_file_id)
    
    bot.send_photo(admin_id,update.message.photo)
    return ConversationHandler.END

def get_text(update, context):
    sender_name = update.message.from_user.username
    msgtext = update.message.text
    unixtime = update.message.date
    datestr = unixtime.strftime("%d-%m-%Y %H-%M-%S")
    fulltext = 'At date ' + datestr + ', ' + sender_name + ' sent this message: ' + '\n' + msgtext
    bot.send_message(chat_id = admin_id, text = fulltext)
    return ConversationHandler.END







ask_handler = ConversationHandler(
        entry_points=[CommandHandler('ask', send_ask_advice)],

        states={
            GET_IMG: [MessageHandler(Filters.photo, get_img),
                      MessageHandler(Filters.text, get_text)]

        },
        fallbacks=[MessageHandler(Filters.document, send_reply_upload_advice),
                   CommandHandler('ask', send_ask_advice)]
    )