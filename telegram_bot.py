from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# 配置你的 OpenAI 和 Telegram Token
openai.api_key = 'YOUR_OPENAI_API_KEY'
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello, I am a chat bot. How can I assist you today?')

def respond(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    response = openai.Completion.create(engine="text-davinci-002", prompt=message, max_tokens=150)
    update.message.reply_text(response.choices[0].text.strip())

def main() -> None:
    updater = Updater(token=TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
