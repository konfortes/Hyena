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

import logging
import os
import time

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from notion import Notion

load_dotenv()

from telegram import ForceReply, Update
from telegram.bot import BotCommand
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

notion = Notion(os.environ["NOTION_API_TOKEN"])

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(fr"Hi {user.mention_markdown_v2()}\!", reply_markup=ForceReply(selective=True))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def digest_text(update: Update, context: CallbackContext) -> None:
    """Digests text messages into Notion GTD inbox"""
    # update.message.reply_text(update.message.text)
    notion.add_page(update.message.text, os.environ["NOTION_DATABASE_ID"])


def digest_voice(update: Update, context: CallbackContext) -> None:
    """Digests voice messages into Notion GTD inbox"""
    file_id = update.message.voice.file_id
    logging.info(f"Downloading {file_id}")
    file = context.bot.get_file(file_id)
    file_name = f"{time.time()}.ogg"
    file.download(file_name)
    logging.info(f"uploading {file_name} to S3")
    s3 = boto3.client("s3")
    try:
        s3.upload_file(file_name, os.environ["AWS_BUCKET_NAME"], file_name)
    except ClientError as e:
        logging.error(e)
    logging.info(f"removing {file_name} from local disk")
    os.remove(file_name)

    logging.info(f"transcribing...")


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

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
