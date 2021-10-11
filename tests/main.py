import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import unittest
import time

import watchcat.__main__
import watchcat.info
from watchcat.notifier.command import CommandNotifier
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.resource.http_resource import HttpResource
from watchcat.snapshot import Snapshot


class Test(unittest.TestCase):
    def test_main(self):
        watchcat.__main__.main()

    def test_http_resource(self):
        pass

    def test_slack_webhook(self):
        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        slack = SlackWebhookNotifier(webhook_url=webhook_url)
        slack.send(f"this is test message from {watchcat.info.name}")

    def test_command_notifier(self):
        command = "echo $message"
        notifier = CommandNotifier(command=command)
        ret = notifier.send(
            f"[test_command_notifier] this is test message from {watchcat.info.name}"
        )
        assert ret == 0

    def test_create_snapshot(self):
        Snapshot("test", time.time(), "this is content")


if __name__ == "__main__":
    unittest.main()
