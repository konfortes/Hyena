from functools import lru_cache
import os


@lru_cache
def get_config():
    return Config(
        env=os.getenv("RUN_ENV", "development"),
        port=os.getenv("PORT", "8080"),
        telegram=TelegramConfig(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            webhook_url=os.getenv("TELEGRAM_WEBHOOK_URL", "localhost"),
        ),
        notion=NotionConfig(
            api_token=os.environ["NOTION_API_TOKEN"], database_id=os.environ["NOTION_DATABASE_ID"]
        ),
        aws=AWSConfig(
            key_id=os.environ["AWS_ACCESS_KEY_ID"],
            secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            default_region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            bucket_name=os.environ["AWS_BUCKET_NAME"],
        ),
    )


class TelegramConfig:
    def __init__(self, bot_token, webhook_url):
        self.bot_token = bot_token
        self.webhook_url = webhook_url


class NotionConfig:
    def __init__(self, api_token, database_id):
        self.api_token = api_token
        self.database_id = database_id


class AWSConfig:
    def __init__(self, key_id, secret_access_key, default_region, bucket_name):
        self.key_id = key_id
        self.secret_access_key = secret_access_key
        self.default_region = default_region
        self.bucket_name = bucket_name


class Config:
    def __init__(self, env, port, telegram: TelegramConfig, notion: NotionConfig, aws: AWSConfig):
        self.env = env
        self.port = port
        self.telegram = telegram
        self.notion = notion
        self.aws = aws
