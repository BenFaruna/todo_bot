import logging
import re

from datetime import datetime

import telegram
from telegram.ext import (
    Updater, CommandHandler, ConversationHandler,
    MessageHandler, Filters, CallbackContext
)

from dbhelper import DBHelper

db = DBHelper()

file = open('token.txt', 'r')
TOKEN = file.read()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

CHOOSING, TYPING_REPLY, DATE_REPLY, ACTION, VIEW = range(5)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hi, I'm your favourite personal assistant here to assist you with keeping "
                                  "your tasks together and keeping you up to date.")


todo_item = dict()


def organizer(update, context: CallbackContext):
    """
    Handles the todo functionality of the bot.
    Bot is able to carry out CRUD functionality with a simple database.
    """

    kb = [[telegram.KeyboardButton('/add'),
           telegram.KeyboardButton('/delete')],
          [telegram.KeyboardButton('/update'),
           telegram.KeyboardButton('/view')]]

    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Hi, thanks for contacting me today, what can I do for you?', reply_markup=kb_markup)
    return CHOOSING


def add_todo(update, context: CallbackContext):
    # Todo: Adds items to the database
    update.message.reply_text(
        "Tell me what you would like to add to your tasks."
    )
    return DATE_REPLY


def view_todo(update, context):
    # Todo: View all user tasks in the database
    items = db.get_items(update.effective_chat.id)
    kb, task, count = [], [], 0
    for item in items:
        task.append(telegram.KeyboardButton(item[0]))

        if count < 1:
            count += 1
        else:
            kb.append(task)
            task, count = [], 0

        if item == items[-1]:
            kb.append([telegram.KeyboardButton(item[0])])

    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)

    context.bot.send_message(chat_id=update.effective_chat.id, text="""
    These are the tasks you have lined up, you can delete or update by selecting from the list.
""", reply_markup=kb_markup)
    return CHOOSING


def update_todo(update, context):
    pass


def delete_todo(update, context: CallbackContext):
    # Todo: deletes items from todo list
    task = todo_item["task"]
    chat_id = update.effective_chat.id
    db.delete_item(chat_id, task)
    del (todo_item["task"])
    update.message.reply_text("""Task has been successfully deleted.
Pick an action(/add, /view, /delete, /update) or send /cancel to quit todo functionality
""")
    return CHOOSING


def date_calendar(update, context):
    todo_item["task"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Enter the deadline for {}".format(todo_item["task"]))
    return ACTION


def add_update(update, context):
    chat_id = update.effective_chat.id
    task = todo_item["task"]
    try:
        todo_item["deadline"] = int(update.message.text)
    except ValueError:
        logging.info("User input data type that's not an integer")
        update.message.reply_text("Enter your date in the correct format dd/mm/yy/ e.g. 12/06/1999")
        return ACTION

    deadline = todo_item["deadline"]

    db.add_item(chat_id, task, deadline)
    del (todo_item["task"])
    del (todo_item["deadline"])
    update.message.reply_text("""
    Task successfully added.
Send /organizer to perform other tasks on your todo list.""")
    return ConversationHandler.END


def action(update, context):
    todo_item["task"] = update.message.text
    update.message.reply_text(
        "Pick an action you want to carry out /update or /delete on {}.".format((todo_item["task"]).upper()))
    return ACTION


def done(update, context):
    if re.search('^[Dd]one$', update.message.text):
        update.message.reply_text("""
    What else would you like to do /add, /view, /update, /delete.
/cancel if you're done using the todo function for now.
    """)
        return CHOOSING
    elif update.message.text == "/cancel":
        update.message.reply_text(
            "Don't forget to come back when you need me. Send /organizer to get me running again.")
        return ConversationHandler.END


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    db.setup()
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)

    organizer_handler = ConversationHandler(
        entry_points=[CommandHandler('organizer', organizer)],
        states={
            CHOOSING: [
                CommandHandler('add', add_todo),
                CommandHandler("view", view_todo),
                CommandHandler("cancel", done),
                MessageHandler(Filters.regex('^[Dd]one$'), done),
                MessageHandler(Filters.text & (~Filters.command), action)

            ],
            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), add_todo)
            ],
            DATE_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), date_calendar)
            ],
            ACTION: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), add_update),
                CommandHandler("delete", delete_todo)
            ],
        },
        fallbacks=[MessageHandler(Filters.regex("^Done$"), done),
                   CommandHandler("cancel", done)],
    )

    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)

    dispatcher.add_handler(organizer_handler)

    dispatcher.add_handler(unknown_handler)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
