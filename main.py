from telegram import Update, MessageHandler, Filters
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TELEGRAM_TOKEN
from handlers import start, respond

if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    updater.start_polling()
    updater.idle()
