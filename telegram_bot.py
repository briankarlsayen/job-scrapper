from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
import requests

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
bot_chat_id = os.getenv("BOT_CHAT_ID")

# poll the message sent to telegram
def bot_polling():
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hello! This message was sent by the bot."
        )
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

# send message to telegram
def send_bot_message(message: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={
        "chat_id": bot_chat_id,
        "text": message
    })