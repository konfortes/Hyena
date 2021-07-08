# Hyena

![hyena](./public/hyena.jpeg)

Hyena is a telegram bot that helps to digest visual and vocal input into Notion's GTD inbox.

## Run

Hyena will run either in push mode (webhook) or in pull mode (polling) based on the `RUN_ENV` config (production=push)  
When set to push mode, the env var `TELEGRAM_WEBHOOK_URL` must be supplied and will be used to register the webhook with the bot.

```bash
pipenv install

python hyena/main.py
```

## Environment Variables

Some env vars should be set in order for the bot to function:

- `RUN_ENV`: the environment the app runs in [development|production]
- `PORT`: The port to listen on when using webhook (production)
- `TELEGRAM_BOT_TOKEN`: The Hyena bot token
- `TELEGRAM_WEBHOOK_URL`: The URL to register the bot to
- `NOTION_API_TOKEN`: The Notion token of the Hyena integration
- `NOTION_DATABASE_ID`: The ID of the inbox database in notion
- `AWS_ACCESS_KEY_ID`: required in order to access AWS Transcribe (and S3)
- `AWS_SECRET_ACCESS_KEY`: required in order to access AWS Transcribe (and S3)
- `AWS_DEFAULT_REGION`: The default AWS region
- `AWS_BUCKET_NAME`: The bucket to save the voice files to before transcribing

## Voice Messages Flow

![voice](./public/hyena_voice_flow.png)
