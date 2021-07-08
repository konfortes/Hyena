"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from hyena.config import get_config
import logging
import os

from dotenv import load_dotenv
from notion import Notion
from voice_handler import VoiceHandler

load_dotenv()

from telegram import ForceReply, Update
from telegram.bot import BotCommand
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

notion = Notion(os.environ["NOTION_API_TOKEN"])

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

config = get_config()

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Hi {user.mention_markdown_v2()}\!", reply_markup=ForceReply(selective=True)
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def digest_text(update: Update, context: CallbackContext) -> None:
    """Digests text messages into Notion GTD inbox"""
    notion.add_page(update.message.text, os.environ["NOTION_DATABASE_ID"])


def digest_voice(update: Update, context: CallbackContext) -> None:
    """Digests voice messages into Notion GTD inbox"""
    voice_handler = VoiceHandler(context.bot, update.message)
    text = voice_handler.handle()

    if text == None or text == "":
        logger.warning("Unable to handle voice message")
        return

    notion.add_page(text, os.environ["NOTION_DATABASE_ID"])


def setCommands(updater: Updater) -> None:
    """Sets the bot commands"""
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    commands = [BotCommand("help", "Get help"), BotCommand("start", "Start conversation")]

    updater.bot.set_my_commands(commands)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ["TELEGRAM_BOT_TOKEN"])

    # on non command i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, digest_text))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, digest_voice))

    setCommands(updater)

    updater.dispatcher.bot

    # Start the Bot
    if config.env == "development":
        updater.start_polling()
    else:
        updater.start_webhook(
            listen="0.0.0.0",
            port=config.port,
            url_path=config.telegram.bot_token,
            webhook_url=f"{config.telegram.webhook_url}/{config.telegram.bot_token}",
        )

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
