from telegram import Update, CallbackContext
from telegram.error import TelegramError
from database import save_message, user_sessions
import openai
import openai.error as openai_error
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
import asyncio
import time

# 创建线程池执行器
executor = ThreadPoolExecutor(max_workers=5)

# 生成图像的同步函数
def generate_image_sync(text, font_file="arial.ttf", image_size=(500, 200)):
    image = Image.new("RGB", image_size, (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, 20)
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    image.save("generated_image.png")

# 生成图像的异步函数
async def generate_image(text, font_file="arial.ttf", image_size=(500, 200)):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor, generate_image_sync, text, font_file, image_size)

# 开始命令的处理函数
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello, I am a chat bot. How can I assist you today?')

# 响应用户消息的处理函数
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
            asyncio.run(generate_image(text))
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
# main function
def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))

    # on non command i.e message - respond the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
