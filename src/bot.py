"""Entrypoint"""
import json
from pathlib import Path

from loguru import logger
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from user_data.database import Database
from user_data.models import UserModels

db = Database()


async def register_user(update, context):
    db.create_user_if_not_exist(update.effective_chat.id)


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a chat-gpt bot.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    input_message = update.message.text
    model = models.get_model(update.message.chat.id, config["openai_token"])
    response = await model.get_response(input_message)
    logger.info(f"chat_id:{update.message.chat.id}, response:\n{response}")
    await update.message.reply_text(response)


def run_bot():
    """Start the bot."""
    application = Application.builder().token(config["telegram_token"]).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Start listening.")
    application.run_polling()


if __name__ == "__main__":
    with open(Path(__file__).parents[1] / "configs/config.json", "rb") as f:
        config = json.load(f)
    models = UserModels()
    run_bot()
