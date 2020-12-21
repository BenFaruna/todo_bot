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
    allowed_extension = ['jpeg', 'jpg', 'png', 'gif']
    file_extension = ''
    while file_extension not in allowed_extension:
        contents = requests.get('https://random.dog/woof.json').json()
        url = contents['url']
        file_extension = re.search(r'([^.]*)$', url).group(1).lower()

    if file_extension == 'gif':
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=url)
    else:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=url)


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
bop_handler = CommandHandler('bop', bop)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(bop_handler)

updater.start_polling()
