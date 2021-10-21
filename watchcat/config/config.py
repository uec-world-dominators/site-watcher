import os
import os.path
from typing import Dict, Union

import yaml
from requests.auth import AuthBase, HTTPBasicAuth
from watchcat.config.errors import (
    ConfigEmptyError,
    ConfigLoadError,
    ConfigVersionMissmatchError,
    ConfigVersionNotFoundError,
)
from watchcat.notifier.command import CommandNotifier
from watchcat.notifier.notifier import Notifier
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.resource.command_resource import CommandResource
from watchcat.notifier.file import FileNotifier
from watchcat.resource.http_resource import HttpResource
from watchcat.resource.resource import Resource
from watchcat.util import expand_environment_variables, recursive_update


class ConfigLoader:
    def __init__(self, config_path: str, use_environment_variables=True) -> None:
        self.version = "1"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"config file not found {config_path}")

        with open(config_path, "rt", encoding="utf-8") as f:
            content = f.read()
            if use_environment_variables:
                content = expand_environment_variables(content)
            config = yaml.load(content, yaml.FullLoader)
            if not config:
                raise ConfigEmptyError()

        self._load_config(config)

    def _load_config(self, config: Dict[str, Dict]):
        # load version
        if version := config.get("version"):
            if version != self.version:
                raise ConfigVersionMissmatchError()
        else:
            raise ConfigVersionNotFoundError()

        # load notifiers
        if notifiers_config := config.get("notifiers"):
            self.notifiers = self._load_notifiers(notifiers_config)
        else:
            self.notifiers = dict()
        self.default_notifier = config.get("default_notifier")

        # load templates
        if templates_config := config.get("templates"):
            self.templates = self._load_templates(templates_config)
        else:
            self.templates = dict()

        # load resources
        if resources_config := config.get("resources"):
            self.resources = self._load_resources(resources_config)
        else:
            self.resources = dict()

    def _get_notifier(self, notifier_id: Union[str, None]) -> Notifier:
        try:
            if not self.notifiers:
                raise ConfigLoadError("You need to set `notifiers`")
            if notifier_id:
                return self.notifiers[notifier_id]
            else:
                if self.default_notifier:
                    return self.notifiers[self.default_notifier]
                else:
                    raise ConfigLoadError("You need to set `default_notifier`")
        except KeyError as e:
            raise ConfigLoadError(f"No such notifier: {e}")

    def _load_notifiers(self, notifiers_config: Dict[str, Dict]) -> Dict[str, Notifier]:
        if not isinstance(notifiers_config, dict):
            raise ConfigLoadError("`notifiers` must be dict")

        notifiers = dict()
        for notifier_key, notifier_config in notifiers_config.items():
            notifier = self._load_notifier(notifier_key, notifier_config)
            notifiers[notifier_key] = notifier
        return notifiers

    def _load_notifier(self, notifier_id: str, notifier_config: Dict[str, str]) -> Notifier:
        if not isinstance(notifier_config, dict):
            raise ConfigLoadError(f"`notifiers.{notifier_id}` must be dict: {notifier_config}")

        try:
            notifier_type = notifier_config["type"]
            if notifier_type == "slack":
                webhook_url = notifier_config["webhook"]
                return SlackWebhookNotifier(notifier_id, webhook_url)
            elif notifier_type == "cmd":
                command = notifier_config["cmd"]
                return CommandNotifier(notifier_id, command)
            elif notifier_type == "file":
                path = notifier_config["path"]
                return FileNotifier(notifier_id, path)
            else:
                raise ConfigLoadError(f"No such notifier: {notifier_id}")
        except KeyError as e:
            raise ConfigLoadError(f"KeyError on loading notifier: {notifier_id}, key: {e}")

    def _load_resources(self, resources_config: Dict[str, Dict[str, str]]) -> Dict[str, Resource]:
        if not isinstance(resources_config, dict):
            raise ConfigLoadError("`resources` must be dict")

        resources = dict()
        for resource_id, resource_config in resources_config.items():
            resources[resource_id] = self._load_resource(resource_id, resource_config)

        return resources

    def _load_resource(self, resource_id: str, resource_config: Dict[str, str]) -> Resource:
        if not isinstance(resource_config, dict):
            raise ConfigLoadError(f"item of `resources` must be dict: {resource_config}")
        import copy

        # upgrade resource config with template
        if template_id := resource_config.get("template"):
            template = self._get_template(template_id)
            resource_config = recursive_update(copy.deepcopy(template), resource_config)

        title = resource_config.get("title")
        url = resource_config.get("url")
        enabled = resource_config.get("enabled", True)
        notifier_id = resource_config.get("notifier")
        notifier = self._get_notifier(notifier_id)
        env = resource_config.get("env")
        cmd = resource_config.get("cmd")
        if auth_config := resource_config.get("auth"):
            auth = self._load_auth(auth_config)
        else:
            auth = None

        if not ((url is not None) ^ ((cmd or env) is not None)):
            raise ConfigLoadError(f"we couldn't determine resource type: {resource_config}")

        if url:
            return HttpResource(
                resource_id=resource_id, notifier=notifier, url=url, enabled=enabled, title=title, auth=auth
            )
        elif cmd:
            return CommandResource(
                resource_id=resource_id, notifier=notifier, cmd=cmd, env=env or dict(), enabled=enabled, title=title
            )
        else:
            raise NotImplementedError()

    def _get_template(self, template_id: str) -> Dict[str, Dict]:
        if self.templates:
            try:
                return self.templates[template_id]
            except KeyError:
                raise ConfigLoadError(f"No such template: {template_id}")
        else:
            raise ConfigLoadError("You need to set `templates`")

    def _load_templates(self, templates_config: Dict[str, Dict]) -> Dict[str, Dict]:
        if not isinstance(templates_config, dict):
            raise ConfigLoadError(f"`templates` must be dict")
        templates = dict()
        for template_key, template_config in templates_config.items():
            templates[template_key] = template_config
        return templates

    def _load_auth(self, auth_config: Dict[str, Dict]) -> AuthBase:
        if not isinstance(auth_config, dict):
            raise ConfigLoadError(f"`auth` must be dict: {auth_config}")

        if basic := auth_config.get("basic"):
            try:
                username = basic["username"]
                password = basic["password"]
                return HTTPBasicAuth(username, password)
            except Exception:
                raise ConfigLoadError(f"format error on basic auth config: {basic}")
        else:
            raise ConfigLoadError(f"Unsupported authentication method")
