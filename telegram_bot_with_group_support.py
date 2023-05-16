from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import os
import time
import json
from PIL import Image, ImageDraw, ImageFont
import sqlite3

# Define commands and responses as constants
GENERATE_IMAGE_COMMAND = "/generate_image"
WHO_ARE_YOU = "Who are you?"
BOT_RESPONSE = "I am a friendly chat bot. I'm here to assist you with any questions you have. How can I help you today?"

# 配置你的 OpenAI 和 Telegram Token
openai.api_key = 'YOUR_OPENAI_API_KEY'
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'

# 为每个用户创建一个会话ID以管理多轮对话
user_sessions = {}

def generate_image(text):
    image = Image.new("RGB", (500, 200), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    image.save("generated_image.png")

def save_message(chat_id, user_id, message):
    with sqlite3.connect('user_messages.db') as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS user_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER, message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cursor.execute('INSERT INTO user_messages (chat_id, user_id, message) VALUES (?, ?, ?)', (chat_id, user_id, message))

def get_messages(chat_id, limit=None):
    with sqlite3.connect('user_messages.db') as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM user_messages WHERE chat_id = ? ORDER BY timestamp DESC'
        if limit is not None:
            query += ' LIMIT {}'.format(limit)
        cursor.execute(query, (chat_id,))
        return cursor.fetchall()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello, I am a chat bot. How can I assist you today?')

def respond(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    save_message(chat_id, user_id, message)

    if update.message.from_user.is_bot:
        return

    if chat_id not in user_sessions:
        user_sessions[chat_id] = f"{chat_id}-{time.time()}"

    session_id = user_sessions[chat_id]

    if message.startswith(GENERATE_IMAGE_COMMAND):
        text = message.replace(GENERATE_IMAGE_COMMAND, "").strip()
        generate_image(text)
        context.bot.send_photo(chat_id=chat_id, photo=open("generated_image.png", "rb"))
    else:
        if WHO_ARE_YOU in message:
            response = BOT_RESPONSE
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "                    "user", "content": message},
                    {"role": "custom", "content": "Custom Role Content"}
                ],
                session_id=session_id,
            )
            response = response['choices'][0]['message']['content']

        context.bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=update.message.message_id)

def save_session_data() -> None:
    with open("session_data.json", "w") as f:
        json.dump(user_sessions, f)

def load_session_data() -> None:
    global user_sessions
    try:
        with open("session_data.json", "r") as f:
            user_sessions = json.load(f)
    except FileNotFoundError:
        user_sessions = {}

def error_handler(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Oops! An error occurred. Please try again later.")

def main() -> None:
    load_session_data()

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(error_handler)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

