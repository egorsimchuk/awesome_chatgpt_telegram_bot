from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import MessageHandler, Filters
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


if __name__ == '__main__':


    updater = Updater('1677667809:AAHH2KzZBHJl4NPS8Jqjrw4bMl6VYviQ8ac')

    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)



    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)


    def caps(update, context):
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
    caps_handler = CommandHandler('caps', caps)
    dispatcher.add_handler(caps_handler)


    def unknown(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sorry, I didn't understand that command.")
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()