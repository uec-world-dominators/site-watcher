import os
import sys

TEST_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(TEST_DIR))
import os.path
import time
import unittest

import watchcat.__main__
import watchcat.info
from watchcat.config.config import ConfigLoader
from watchcat.config.errors import ConfigEmptyError, ConfigVersionMissmatchError
from watchcat.notifier.command import CommandNotifier
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.resource.command_resource import CommandResource
from watchcat.resource.http_resource import HttpResource
from watchcat.snapshot import Snapshot


class Test(unittest.TestCase):
    # def test_main(self):
    #     watchcat.__main__.main()

    def test_http_resource(self):
        http_resource = HttpResource("google", None, "https://www.google.com", title="Google")
        snapshot = http_resource.get()
        assert snapshot.resource_id == "google"

    def test_command_resource(self):
        command_resource = CommandResource("echo", None, "echo $var", env={"var": "hoge"})
        assert command_resource.get() == "hoge\n"

    def test_slack_webhook(self):
        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        slack = SlackWebhookNotifier("slack1", webhook_url=webhook_url)
        slack.send(f"this is test message from {watchcat.info.name}")

    def test_command_notifier(self):
        command = "echo $message"
        notifier = CommandNotifier("command1", command=command)
        ret = notifier.send(f"[test_command_notifier] this is test message from {watchcat.info.name}")
        assert ret == 0

    def test_create_snapshot(self):
        Snapshot("test", time.time(), "this is content")


class ConfigTest(unittest.TestCase):
    def test_config_loader_all(self):
        ConfigLoader(os.path.join(TEST_DIR, "configs/all.yaml"))

    def test_config_loader_empty(self):
        try:
            ConfigLoader(os.path.join(TEST_DIR, "configs/empty.yaml"))
            raise RuntimeError()
        except ConfigEmptyError:
            return

    def test_config_loader_version_only(self):
        ConfigLoader(os.path.join(TEST_DIR, "configs/version_only.yaml"))

    def test_config_loader_version_missmatch(self):
        try:
            ConfigLoader(os.path.join(TEST_DIR, "configs/version_missmatch.yaml"))
            raise RuntimeError()
        except ConfigVersionMissmatchError:
            return


if __name__ == "__main__":
    unittest.main()
