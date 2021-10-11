import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
import watchcat.__main__
import watchcat.info
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.notifier.command import CommandNotifier


class Test(unittest.TestCase):
    def test_main(self):
        watchcat.__main__.main()

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


if __name__ == "__main__":
    unittest.main()
