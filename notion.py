import requests
import os

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2021-05-13"


class Notion:
    def __init__(self, token: str):
        self.token = token

    def add_page(self, content: str, parentDatabase: str):
        payload = {
            "parent": {"database_id": parentDatabase},
            "properties": {"title": {"title": [{"text": {"content": content}}]}},
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

        res = requests.post(
            NOTION_API_URL,
            json=payload,
            headers=headers,
        )

        # TODO: error handling
        print(res.json())
