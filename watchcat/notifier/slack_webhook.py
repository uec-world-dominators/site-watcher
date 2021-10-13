import sys
from watchcat.notifier.errors import NotificationError
from .notifier import Notifier
import requests


class SlackWebhookNotifier(Notifier):
    def __init__(self, _id: str, webhook_url: str) -> None:
        super().__init__(_id)
        self.webhook_url = webhook_url

    def send(self, message: str):
        res = requests.post(self.webhook_url, json={"text": message,},)
        if res.status_code == 200:
            return
        else:
            print(res.text, file=sys.stderr)
            raise NotificationError()

    def __repr__(self) -> str:
        return f"<SlackWebhookNotifier(webhook_url={self.webhook_url})>"
