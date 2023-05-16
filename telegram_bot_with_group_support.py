from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import os
import time
import json
from PIL import Image, ImageDraw, ImageFont
import sqlite3

# 配置你的 OpenAI 和 Telegram Token
openai.api_key = 'YOUR_OPENAI_API_KEY'
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'

# 图片生成函数
def generate_image(text):
    image = Image.new("RGB", (500, 200), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    image.save("generated_image.png")

# 为每个用户创建一个会话ID以管理多轮对话
user_sessions = {}

def save_message(chat_id, user_id, message):
    # 将消息保存到数据库
    with sqlite3.connect('user_messages.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_messages (chat_id, user_id, message) VALUES (?, ?, ?)', (chat_id, user_id, message))
        conn.commit()

def get_messages(chat_id, limit=None):
    # 获取指定聊天ID的消息，按时间倒序排序
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

    save_message(chat_id, user_id, message)  # 保存用户消息到数据库

    # 如果是在群聊中，检查消息是否是由机器人自身发送的
    if update.message.from_user.is_bot:
        return

    # 如果用户是新的，创建一个新的会话ID
    if chat_id not in user_sessions:
        user_sessions[chat_id] = f"{chat_id}-{time.time()}"

    session_id = user_sessions[chat_id]

    if message.startswith("/generate_image"):
        # 获取要生成图片的文字内容
        text = message.replace("/generate_image", "").strip()

        if text:  # 添加了输入验证
            # 调用生成图片的函数
            generate_image(text)

            # 发送生成的图片给用户
            context.bot.send_photo(chat_id=chat_id, photo=open("generated_image.png", "rb"))
        else:
            context.bot.send_message(chat_id=chat_id, text="Please provide some text after the command.")
    else:
        if "Who are you?" in message:
            response = "I am a friendly chat bot. I'm here to assist you with any questions you have. How can I help you today?"
        else:
            # 使用 Chat API 进行会话
            response = openai.ChatCompletion.create(
                model="gpt-4",  # 更改为新的模型
                messages=[
                                        {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ],
                session_id=session_id
            ).choices[0].message['content']

        # 发送回复给用户
        update.message.reply_text(response)

# main函数
def main() -> None:
    updater = Updater(token=TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
