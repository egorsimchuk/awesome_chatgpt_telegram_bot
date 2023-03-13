"""Entrypoint"""
import json
from pathlib import Path

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

from user_data.database import Database
from user_data.models import UserModels

HELP_MESSAGE = """Commands:
/start - Start bot
/set_api_key – Set your openai api key
/help – Show help
"""


async def register_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db.create_user_if_not_exist(chat_id, update.effective_chat.username)
    if db.get_openai_api_key(chat_id) is None:
        await context.bot.send_message(chat_id=chat_id, text="Please set your openai api key with /set_api_key your_key")


async def set_openai_api_key(update: Update, context: CallbackContext):
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML,
            text="Enter your key after /set_api_key. For example:\n<pre>/set_api_key lol-YouRKeYBroWtF</pre>",
        )
    else:
        db.set_openai_api_key(update.effective_chat.id, context.args[0])
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Openai api key is updated")


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a chat-gpt bot." + " ".join(context.args))
    await register_user(update, context)


async def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    chat_id = update.effective_chat.id
    model = models.get_model(chat_id, db.get_openai_api_key(chat_id))
    response = model.get_response(update.message.text)
    logger.info(f"chat_id:{chat_id}, response:\n{response}")
    await update.message.reply_text(response)


async def help_handler(update: Update, context: CallbackContext):
    db.update_interaction_timestamp(update.effective_chat.id)
    await update.message.reply_text(HELP_MESSAGE)


def run_bot():
    """Start the bot."""
    application = Application.builder().token(config["telegram_token"]).build()

    if len(config["allowed_users"]) == 0:
        user_filter = filters.ALL
    else:
        user_filter = filters.User(username=config["allowed_users"])

    application.add_handler(CommandHandler("start", start, filters=user_filter))
    application.add_handler(CommandHandler("set_api_key", set_openai_api_key, filters=user_filter))
    application.add_handler(CommandHandler("help", help_handler, filters=user_filter))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND & user_filter, callback=echo))

    logger.info("Start listening.")
    application.run_polling()


if __name__ == "__main__":
    with open(Path(__file__).parents[1] / "configs/config.json", "rb") as f:
        config = json.load(f)
    models = UserModels()
    db = Database()
    run_bot()
