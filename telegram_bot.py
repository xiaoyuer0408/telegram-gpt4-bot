from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import os

# 配置你的 OpenAI 和 Telegram Token
openai.api_key = os.getenv('OPENAI_API_KEY')
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
        model="gpt-3.5-turbo",  # 更换为你选择的模型
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
        session_id=session_id,
    )
    update.message.reply_text(response['choices'][0]['message']['content'])

def main() -> None:
    updater = Updater(token=TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
