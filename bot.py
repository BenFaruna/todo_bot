import logging
import re
import requests

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


def bop(update, context):
    contents = requests.get('https://random.dog/woof.json').json()
    img_url = contents['url']
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_url)


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
bop_handler = CommandHandler('bop', bop)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(bop_handler)

updater.start_polling()
