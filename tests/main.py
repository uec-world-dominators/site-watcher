import os
import sys

TEST_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(TEST_DIR))
import os.path
import time
import unittest
import requests

import watchcat.__main__
import watchcat.info
from watchcat import util
from watchcat.config.config import ConfigLoader
from watchcat.config.errors import ConfigEmptyError, ConfigVersionMissmatchError
from watchcat.notifier.command import CommandNotifier
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.notifier.slack_bot import SlackBotNotifier
from watchcat.notifier.file import FileNotifier
from watchcat.resource.command_resource import CommandResource
from watchcat.resource.http_resource import HttpResource
from watchcat.snapshot import Snapshot
from watchcat.storage.sql_storage import SqlStorage
from watchcat.filter.command import CommandFilter
from watchcat.filter.css_selector import CssSelectorFilter


class Test(unittest.TestCase):
    # def test_main(self):
    #     watchcat.__main__.main()

    def test_http_resource(self):
        resource_id = "google"
        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        notifier = SlackWebhookNotifier("slack1", webhook_url=webhook_url)
        url = "https://www.google.com"
        title = "Google"

        http_resource = HttpResource(resource_id, notifier, url, title=title)
        snapshot = http_resource._get()
        assert snapshot.resource_id == resource_id
        assert http_resource.title == title

        http_resource2 = HttpResource(resource_id, notifier, url)
        snapshot2 = http_resource2._get()
        assert snapshot2.resource_id == resource_id
        assert http_resource2.title == url

    def test_command_resource(self):
        resource_id = "echo"
        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        notifier = SlackWebhookNotifier("slack1", webhook_url=webhook_url)
        cmd = "echo $var"
        title = "echo"

        command_resource = CommandResource(resource_id, notifier, cmd, env={"var": "hoge"}, title=title)
        snapshot = command_resource._get()
        assert snapshot.resource_id == resource_id
        assert command_resource.title == title

        command_resource2 = CommandResource(resource_id, notifier, cmd, env={"var": "hoge"})
        snapshot2 = command_resource2._get()
        assert snapshot2.resource_id == resource_id
        assert command_resource2.title == cmd

    def test_slack_webhook(self):
        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        slack = SlackWebhookNotifier("slack1", webhook_url=webhook_url)
        slack.send(f"this is test message from {watchcat.info.name}", "description", "+ hoge\n- hoge")

    def test_slack_bot(self):
        token = os.environ["SLACK_TOKEN"]
        channel = os.environ["SLACK_CHANNEL"]
        slack = SlackBotNotifier("slack1", token, channel)
        slack.send(f"this is test message from {watchcat.info.name}", "description", "+ hoge\n- hoge")

    def test_command_notifier(self):
        command = "echo $diff"
        notifier = CommandNotifier("command1", command=command)
        ret = notifier.send(
            f"[test_command_notifier] this is test message from {watchcat.info.name}", "description", "diff"
        )
        assert ret == 0

    def test_create_snapshot(self):
        Snapshot("test", time.time(), "this is content")

    def test_sql_storage(self):
        sql = SqlStorage("test.db")
        content1 = "this 'is' content"
        snapshot = Snapshot("test", time.time(), content1)
        sql.set(snapshot)
        content2 = sql.get("test").content
        assert content1 == content2


class UtilTest(unittest.TestCase):
    def test_expand_environment_variable(self):
        os.environ["HOGE"] = "123"
        s = r"ab${{HOGE}}cd"
        s = util.expand_environment_variables(s)
        self.assertEqual(s, "ab123cd")

    def test_expand_environment_variable_empty_before(self):
        os.environ["HOGE"] = "123"
        s = r"${{HOGE}}cd"
        s = util.expand_environment_variables(s)
        self.assertEqual(s, "123cd")

    def test_expand_environment_variable_empty_after(self):
        os.environ["HOGE"] = "123"
        s = r"ab${{HOGE}}"
        s = util.expand_environment_variables(s)
        self.assertEqual(s, "ab123")

    def test_expand_environment_variable_empty_both(self):
        os.environ["HOGE"] = "123"
        s = r"${{HOGE}}"
        s = util.expand_environment_variables(s)
        self.assertEqual(s, "123")

    def test_expand_environment_variable_multiple(self):
        os.environ["HOGE"] = "123"
        os.environ["HAGE"] = "456"
        s = r"${{HOGE}}${{HAGE}}"
        s = util.expand_environment_variables(s)
        self.assertEqual(s, "123456")


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


class FilterTest(unittest.TestCase):
    def test_command_filter(self):
        filter = CommandFilter("grep hoge")
        _in = "hoge\nhage\nhige\n"
        out = filter.filter(_in)
        self.assertEqual(out, "hoge\n")

    def test_cssselector_filter(self):
        filter = CssSelectorFilter("#hoge")
        _in = '<html><body><div id="hoge"></div></body></html>'
        out = filter.filter(_in)
        self.assertEqual(out, '<div id="hoge"></div>')


class EncodingTest(unittest.TestCase):
    def test_meta_charset(self):
        url = "http://www.hpc.is.uec.ac.jp/jikken2/2021webpage.html"
        notifier = FileNotifier("test", "/dev/stdout")
        resource = HttpResource("test", notifier, url)
        charset = resource._determine_encoding(requests.get(url))
        assert charset == "UTF-8"

    def test_content_type_header(self):
        url = "https://stackoverflow.com/"
        notifier = FileNotifier("test", "/dev/stdout")
        resource = HttpResource("test", notifier, url)
        charset = resource._determine_encoding(requests.get(url))
        assert charset == "utf-8"


if __name__ == "__main__":
    unittest.main()
