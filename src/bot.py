"""Entrypoint"""
import json
from typing import Union

from loguru import logger
from openai.error import AuthenticationError
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

from user_data.database import Database
from user_data.models import UserModels
from utils import get_path_from_root_dir, utc_now

HELP_MESSAGE = """Commands:
/set_api_key – Set your openai api key
/start_new_chat - Start new chat with assistant
/chat_modes - Available chat modes
/help – Show help
"""

CHAT_TIMEOUT_SEC = 60 * 30
DEFAULT_MODE = "assistant"
with open(get_path_from_root_dir("configs/config.json"), "rb") as f:
    config = json.load(f)
with open(get_path_from_root_dir("configs/chat_modes.json"), "rb") as f:
    chat_modes = json.load(f)
CHAT_MODES_STR = "/" + "\n/".join(list(chat_modes.keys()))
models = UserModels()
db = Database()


async def register_user(update: Update, context: CallbackContext, openai_api_key: str = None):
    chat_id = update.effective_chat.id
    db.create_user_if_not_exist(chat_id, update.effective_chat.username)
    openai_api_key = openai_api_key or db.get_openai_api_key(chat_id)
    if openai_api_key is None:
        await context.bot.send_message(chat_id=chat_id, text="Please set openai api key with /set_api_key command.")


async def set_openai_api_key(update: Update, context: CallbackContext):
    await register_user(update, context)
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=ParseMode.HTML,
            text="Enter your key after /set_api_key. For example:\n/set_api_key lol-YouRKeYBroWtF",
        )
    else:
        db.set_openai_api_key(update.effective_chat.id, context.args[0])
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Openai api key was updated.")


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🧠 Welcome to chat-gpt bot 🤖\n{HELP_MESSAGE}")
    await register_user(update, context)


async def switch_mode(update, context):
    await register_user(update, context)
    chat_id = update.effective_chat.id
    model = models.get_model(chat_id, db.get_openai_api_key(chat_id))
    mode = update.message.text[1:]
    promt = chat_modes[mode]["promt"]
    model.switch_mode(promt)
    db.update_interaction_timestamp(chat_id)
    await context.bot.send_message(chat_id=chat_id, text=f"💭 Chat mode switched to {mode}. ⚙️Promt:\n{promt}")


async def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    chat_id = update.effective_chat.id
    openai_api_key = db.get_openai_api_key(chat_id)
    await register_user(update, context, openai_api_key)
    model = models.get_model(chat_id, openai_api_key)

    if utc_now() - db.get_last_interaction_timestamp(chat_id) > CHAT_TIMEOUT_SEC:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🍌 New chat with assistant started after {round(CHAT_TIMEOUT_SEC/60)} minutes since last message.",
        )
        model.switch_mode(chat_modes[DEFAULT_MODE]["promt"])
    if not model.conversation_initialized:
        model.switch_mode(chat_modes[DEFAULT_MODE]["promt"])

    db.update_interaction_timestamp(chat_id)
    response = model.get_response(update.message.text)
    await model_response_handler(response, update, context)


async def start_new_chat(update: Update, context: CallbackContext):
    await register_user(update, context)
    chat_id = update.effective_chat.id
    model = models.get_model(chat_id, db.get_openai_api_key(chat_id))
    model.switch_mode(chat_modes[DEFAULT_MODE]["promt"])
    db.update_interaction_timestamp(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="🍌 New chat with assistant started.")


async def model_response_handler(response: Union[str, Exception], update: Update, context: CallbackContext):
    if isinstance(response, Exception):
        if isinstance(response, AuthenticationError):
            await update.message.reply_text(f"Set correct openai api key with /set_api_key.\n\n{response.error.message}")
        else:
            await update.message.reply_text(f"Not handled error, please contact developer.\n\n{response.error.message}")
    else:
        await update.message.reply_text(response)


async def help_handler(update: Update, context: CallbackContext):
    await update.message.reply_text(HELP_MESSAGE)


async def chat_modes_handler(update: Update, context: CallbackContext):
    await update.message.reply_text(CHAT_MODES_STR)


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
    application.add_handler(CommandHandler("chat_modes", chat_modes_handler, filters=user_filter))
    application.add_handler(CommandHandler("start_new_chat", start_new_chat, filters=user_filter))
    application.add_handler(CommandHandler(list(chat_modes.keys()), switch_mode, filters=user_filter))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND & user_filter, callback=echo))

    logger.info("Start listening.")
    application.run_polling()


if __name__ == "__main__":
    run_bot()
