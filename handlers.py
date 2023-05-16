from telegram import Update, CallbackContext
from image_gen import generate_image
from database import save_message, user_sessions
import openai

def start(update: Update, context: CallbackContext) -> None:
    """
    Telegram 机器人的 /start 命令处理程序
    参数：
        update - 更新对象，包含有关当前更新的信息
        context - 回调上下文对象，用于处理与 Telegram API 的交互
    """
    update.message.reply_text('你好，我是一个聊天机器人。今天我能帮你做什么？')

def respond(update: Update, context: CallbackContext) -> None:
    """
    Telegram 机器人的消息处理程序
    参数：
        update - 更新对象，包含有关当前更新的信息
        context - 回调上下文对象，用于处理与 Telegram API 的交互
    """
    message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    save_message(chat_id, user_id, message)

    if update.message.from_user.is_bot:
        return

    if chat_id not in user_sessions:
        user_sessions[chat_id] = f"{chat_id}-{time.time()}"

    session_id = user_sessions[chat_id]

    if message.startswith("/generate_image"):
        text = message.replace("/generate_image", "").strip()

        if text:
            generate_image(text)
            context.bot.send_photo(chat_id=chat_id, photo=open("generated_image.png", "rb"))
        else:
            context.bot.send_message(chat_id=chat_id, text="请在命令后提供一些文本。")
    else:
        if "你是谁？" in message:
            response = "我是一个友好的聊天机器人。我在这里帮助您解答任何问题。今天我能帮你做什么？"
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ],
                session_id=session_id
            ).choices[0].message['content']

        update.message.reply_text(response)
