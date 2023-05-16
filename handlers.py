from telegram import Update, CallbackContext
from telegram.error import TelegramError
from image_gen import generate_image
from database import save_message, user_sessions
import openai
import openai.error as openai_error

# 开始命令的处理函数
def start(update: Update, context: CallbackContext) -> None:
    """
    当用户发送 /start 命令时调用此函数。
    参数:
        update: Update 对象，包含有关更新的信息。
        context: CallbackContext 对象，用于处理回调的上下文。
    """
    update.message.reply_text('Hello, I am a chat bot. How can I assist you today?')

# 响应用户消息的处理函数
def respond(update: Update, context: CallbackContext) -> None:
    """
    当用户发送文本消息时调用此函数。
    参数:
        update: Update 对象，包含有关更新的信息。
        context: CallbackContext 对象，用于处理回调的上下文。
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
            context.bot.send_message(chat_id=chat_id, text="Please provide some text after the command.")
    else:
        try:
            if "Who are you?" in message:
                response = "I am a friendly chat bot. I'm here to assist you with any questions you have. How can I help you today?"
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": message},
                    ],
                    session_id=session_id
                ).choices[0].message['content']
        except openai_error.OpenAIError as e:
            response = "I'm sorry, but I'm having trouble processing your request. Please try again later."
            print(f"OpenAI API error: {e}")

        try:
            update.message.reply_text(response)
        except TelegramError as e:
            print(f"Telegram API error: {e}")
