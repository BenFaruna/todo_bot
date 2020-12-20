import logging
import re
import requests
from requests.api import get

from telegram.ext import InlineQueryHandler, Updater, CommandHandler, MessageHandler, Filters

file = open('token.txt', 'r')
TOKEN = file.read()


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I'm a bot, please chat with me!")


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)

updater.start_polling()
