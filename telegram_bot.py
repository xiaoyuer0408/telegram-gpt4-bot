from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import os
import time
import json

# 配置你的 OpenAI 和 Telegram Token
openai.api_key = 'YOUR_OPENAI_API_KEY'
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'

# 为每个用户创建一个会话ID以管理多轮对话
user_sessions = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello, I am a chat bot. How can I assist you today?')

def respond(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    chat_id = update.effective_chat.id

    # 如果用户是新的，创建一个新的会话ID
    if chat_id not in user_sessions:
        user_sessions[chat_id] = f"{chat_id}-{time.time()}"

    session_id = user_sessions[chat_id]
    # 使用 Chat API 进行会话
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 更换为你选择的模型
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
        session_id=session_id,
    )
    update.message.reply_text(response['choices'][0]['message']['content'])

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

    # 创建 Updater 对象并设置 Telegram Token
    updater = Updater(token=TELEGRAM_TOKEN)

    # 获取 Dispatcher 对象
    dispatcher = updater.dispatcher

    # 添加处理程序
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    # 添加错误处理程序
    dispatcher.add_error_handler(error_handler)

    # 开始轮询更新
    updater.start_polling()

    # 在程序结束之前保存会话数据
    save_session_data()

    # 进入空闲状态
    updater.idle()

if __name__ == '__main__':
    main()
