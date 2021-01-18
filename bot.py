import logging
import re

from datetime import datetime

import telegram
from telegram.ext import (
    Updater, CommandHandler, ConversationHandler,
    MessageHandler, Filters)

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
                                  "your tasks together and keeping you up to date😉.")


todo_item = dict()


def organizer(update, context):
    """
    Handles the todo functionality of the bot.
    Bot is able to carry out CRUD functionality with a simple database.
    """

    kb = [[telegram.KeyboardButton('/add'),
           telegram.KeyboardButton('/view')]]

    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Hi, thanks for contacting me today, what can I do for you?\n'
                              'Send Done or /cancel at any point to carry out a new task or end Todo function.',
                              reply_markup=kb_markup)
    return CHOOSING


def add_todo(update, context):
    # Todo: Adds items to the database
    update.message.reply_text(
        "Tell me what you would like to add to your tasks."
    )
    return DATE_REPLY


def view_todo(update, context):
    # Todo: View all user tasks in the database
    items = db.get_items(update.effective_chat.id)

    if not items:
        return ConversationHandler.END

    kb, task, count = [], [], 0
    for item in items:
        task.append(telegram.KeyboardButton(item[1]))

        if count < 1:
            count += 1
        else:
            kb.append(task)
            task, count = [], 0

        if item == items[-1] and count % 2 != 0:
            kb.append([telegram.KeyboardButton(item[1])])

    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=update.effective_chat.id, text="""
    These are the tasks you have lined up, you can delete or update by selecting from the list.
Send Done or /cancel at any point to carry out a new task or end Todo function.
""", reply_markup=kb_markup)
    return CHOOSING


def delete_todo(update, context):
    # Todo: deletes items from todo list
    task = todo_item["task"]
    chat_id = update.effective_chat.id
    db.delete_item(chat_id, task)
    del (todo_item["task"])
    update.message.reply_text("""Task has been successfully deleted.
Pick an action(/add, /view) or send /cancel to quit todo functionality
""")
    return CHOOSING


def update_todo(update, context):
    # Todo: updates items in a todo list
    chat_id = update.effective_chat.id
    todo_item["old_task"] = todo_item["task"]
    tasks = db.get_items(chat_id)
    for task in tasks:
        if task[1] == todo_item["old_task"]:
            todo_item["id"] = task[0]
    update.message.reply_text("Enter new task detail for {}".format(todo_item["old_task"].upper()))

    return DATE_REPLY


def date_calendar(update, context):
    todo_item["task"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Enter the deadline for {} in this format DD/MM/YY".format(todo_item["task"]))
    return ACTION


def add_update(update, context):
    chat_id = update.effective_chat.id
    task = todo_item["task"]
    try:
        date_arr = update.message.text.split("/")

        # In cases where short date is passed
        if len(date_arr[2]) == 2:
            date_arr[2] = "20" + date_arr[2]
            logging.info(f"short year provided, changed to {date_arr[2]}")

        todo_item["deadline"] = datetime(int(date_arr[2]), int(date_arr[1]), int(date_arr[0])).timestamp()
    except ValueError as e:
        logging.info(f"day: {date_arr[0]}, month: {date_arr[1]}, year: {date_arr[2]}")
        logging.info(f"{e.__class__.__name__} {e.__str__()}")
        update.message.reply_text("Enter your date in the correct format day/month/year/\n"
                                  "e.g. 12/06/2021.\n"
                                  f"Error: {e.__str__()}")
        return ACTION
    except IndexError:
        update.message.reply_text("Enter your date in the correct format day/month/year/ e.g. 12/06/2021.")
        return ACTION

    deadline = todo_item["deadline"]

    if "old_task" in todo_item:
        try:
            db.update_item(todo_item["id"], task, deadline)
            update.message.reply_text("""
            Task successfully updated from {} to {}.
    Send /organizer to perform other tasks on your todo list.
                """.format(todo_item["old_task"].upper(), todo_item['task'].upper()))
            del (todo_item["task"])
            del(todo_item["old_task"])
            del (todo_item["deadline"])
            return ConversationHandler.END
        except KeyError:
            logging.info(f"Task {todo_item['old_task']} not in database.")
            db.add_item(chat_id, task, deadline)
            return ConversationHandler.END

    else:
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
        "Pick an action you want to carry out /update or /delete on {}."
        "send /cancel to end operation.".format((todo_item["task"]).upper()))
    return ACTION


def done(update, context):
    if re.search('^[Dd]one$', update.message.text):
        update.message.reply_text("""
    What else would you like to do /add, /view.
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
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^[Dd]one$')), add_todo)
            ],
            DATE_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^[Dd]one$')), date_calendar)
            ],
            ACTION: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^[Dd]one$')), add_update),
                CommandHandler("update", update_todo),
                CommandHandler("delete", delete_todo)
            ],
        },
        fallbacks=[MessageHandler(Filters.regex("^[Dd]one$"), done),
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
