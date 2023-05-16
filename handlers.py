from telegram import Update, CallbackContext
from image_gen import generate_image
from database import save_message, user_sessions
import openai

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

    if message.startswith("/generate_image"):
        text = message.replace("/generate_image", "").strip()

        if text:
            generate_image(text)
            context.bot.send_photo(chat_id=chat_id, photo=open("generated_image.png", "rb"))
        else:
            context.bot.send_message(chat_id=chat_id, text="Please provide some text after the command.")
    else:
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

        update.message.reply_text(response)
