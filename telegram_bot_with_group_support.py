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

# 创建数据库连接
conn = sqlite3.connect('user_messages.db')
cursor = conn.cursor()

# 创建用户消息表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        user_id INTEGER,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 为每个用户创建一个会话ID以管理多轮对话
user_sessions = {}

# 图片生成函数
def generate_image(text):
    image = Image.new("RGB", (500, 200), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    image.save("generated_image.png")

def save_message(chat_id, user_id, message):
    # 将消息保存到数据库
    cursor.execute('INSERT INTO user_messages (chat_id, user_id, message) VALUES (?, ?, ?)', (chat_id, user_id, message))
    conn.commit()

def get_messages(chat_id, limit=None):
    # 获取指定聊天ID的消息，按时间倒序排序
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

        # 调用生成图片的函数
        generate_image(text)

        # 发送生成的图片给用户
        context.bot.send_photo(chat_id=chat_id, photo=open("generated_image.png", "rb"))
    else:
        if "Who are you?" in message:
            response = "I am a friendly chat bot. I'm here to assist you with any questions you have. How can I help you today?"
        else:
            # 使用 Chat API 进行会话
            response = openai.ChatCompletion.create(
model="gpt-4", # 更换为你选择的模型
messages=[
{"role": "system", "content": "You are a helpful assistant."},
{"role": "user", "content": message},
{"role": "custom", "content": "Custom Role Content"} # 修改自定义角色的标识符和内容
],
session_id=session_id,
)
response = response['choices'][0]['message']['content']

    # 向该用户发送响应框
    context.bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=update.message.message_id)

    def save_session_data() -> None:
# 保存会话数据到文件
with open("session_data.json", "w") as f:
json.dump(user_sessions, f)

def load_session_data() -> None:
# 从文件加载会话数据
global user_sessions
try:
with open("session_data.json", "r") as f:
user_sessions = json.load(f)
except FileNotFoundError:
user_sessions = {}

def error_handler(update: Update, context: CallbackContext) -> None:
"""处理运行时的错误并发送错误消息给用户"""
update.message.reply_text("Oops! An error occurred. Please try again later.")

def main() -> None:
# 加载之前保存的会话数据
load_session_data()

if name == 'main':
main()
