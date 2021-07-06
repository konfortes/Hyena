import json
import logging
import os
import time
import urllib

import boto3
from botocore.exceptions import ClientError
from telegram.bot import Bot
from transcribe import Transcribe


class VoiceHandler:
    def __init__(self, bot, message, s3=None, transcribe=None):
        self.bot = bot
        self.message = message
        self.s3 = s3 if s3 else boto3.client("s3")
        self.transcribe = transcribe if transcribe else boto3.client("transcribe")

    def handle(self):
        telegram_file_id = self.message.voice.file_id
        local_file_name = f"{time.time()}.ogg"
        try:
            self.__download_telegram_file(telegram_file_id, local_file_name)
        except BaseException as e:
            logging.error(f"Error downloading file: {e}")
            return None

        s3_file_name = local_file_name
        bucket_name = os.environ["AWS_BUCKET_NAME"]
        try:
            self.__upload_to_s3(local_file_name, s3_file_name, bucket_name)
        except ClientError as e:
            logging.error(f"Error uploading to S3: {e}")
            return None
        finally:
            logging.info(f"Removing {local_file_name} from local disk")
            os.remove(local_file_name)

        try:
            text = Transcribe(self.transcribe).transcribe(s3_file_name, bucket_name)
        except BaseException as e:
            logging.error(f"Error Transcribing: {e}")
            return None

        return text

    def __download_telegram_file(self, id: str, output_name: str):
        logging.info(f"Downloading {id} and saving as {output_name}")
        file = self.bot.get_file(id)
        file.download(output_name)

    def __upload_to_s3(self, local_file_name: str, s3_file_name: str, bucket_name: str):
        logging.info(f"Uploading {local_file_name} to S3 as {s3_file_name}")
        self.s3.upload_file(local_file_name, bucket_name, s3_file_name)
