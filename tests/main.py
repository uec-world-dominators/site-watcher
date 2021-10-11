import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import unittest

import watchcat.__main__
import watchcat.info
from watchcat.notifier.command import CommandNotifier
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.resource.command_resource import CommandResource
from watchcat.resource.http_resource import HttpResource


class Test(unittest.TestCase):
    def test_main(self):
        watchcat.__main__.main()

    def test_http_resource(self):
        http_resource = HttpResource("Google", None, "https://www.google.com")
        http_resource.get()

    def test_command_resource(self):
        command_resource = CommandResource("echo", None, "echo $var", env={"var": "hoge"})
        assert command_resource.get() == "hoge\n"

    def test_slack_webhook(self):
        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        slack = SlackWebhookNotifier(webhook_url=webhook_url)
        slack.send(f"this is test message from {watchcat.info.name}")

    def test_command_notifier(self):
        command = "echo $message"
        notifier = CommandNotifier(command=command)
        notifier.send(f"[test_command_notifier] this is test message from {watchcat.info.name}")


if __name__ == "__main__":
    unittest.main()
