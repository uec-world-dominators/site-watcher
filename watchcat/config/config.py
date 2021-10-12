import os.path
from typing import Dict, List, Union
import yaml
from watchcat.config.errors import (
    ConfigEmptyError,
    ConfigLoadError,
    ConfigVersionMissmatchError,
    ConfigVersionNotFoundError,
)
from watchcat.notifier.notifier import Notifier
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.notifier.command import CommandNotifier
from watchcat.resource.resource import Resource
from watchcat.resource.http_resource import HttpResource
from watchcat.resource.command_resource import CommandResource
from watchcat.util import recursive_update


class ConfigLoader:
    def __init__(self, config_path: str) -> None:
        self.version = "1"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"config file not found {config_path}")

        with open(config_path, "rt", encoding="utf-8") as f:
            config = yaml.load(f, yaml.FullLoader)
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
            self.resources = list()

    def _get_notifier(self, notifier_id: Union[str, None]) -> Notifier:
        if not self.notifiers:
            raise ConfigLoadError("You need to set `notifiers`")
        if notifier_id:
            return self.notifiers[notifier_id]
        else:
            if self.default_notifier:
                return self.notifiers[self.default_notifier]
            else:
                raise ConfigLoadError("You need to set `default_notifier`")

    def _load_notifiers(self, notifiers_config: Dict[str, Dict]) -> Dict[str, Notifier]:
        if not isinstance(notifiers_config, dict):
            raise ConfigLoadError(f"`notifiers` must be dict")

        notifiers = dict()
        for notifier_key, notifier_config in notifiers_config.items():
            notifier = self._load_notifier(notifier_key, notifier_config)
            notifiers[notifier_key] = notifier
        return notifiers

    def _load_notifier(
        self, notifier_id: str, notifier_config: Dict[str, str]
    ) -> Notifier:
        if not isinstance(notifier_config, dict):
            raise ConfigLoadError(
                f"`notifiers.{notifier_id}` must be dict: {notifier_config}"
            )

        notifier_type = notifier_config["type"]
        if notifier_type == "slack":
            webhook_url = notifier_config["webhook"]
            return SlackWebhookNotifier(notifier_id, webhook_url)
        elif notifier_type == "cmd":
            command = notifier_config["cmd"]
            return CommandNotifier(notifier_id, command)

    def _load_resources(self, resources_config: List[Dict[str, str]]) -> List[Resource]:
        if not isinstance(resources_config, list):
            raise ConfigLoadError(f"`resources` must be list")

        resources = list()
        for resource_config in resources_config:
            resource = self._load_resource(resource_config)
            resources.append(resource)
        return resources

    def _load_resource(self, resource_config: Dict[str, str]) -> Resource:
        if not isinstance(resource_config, dict):
            raise ConfigLoadError(
                f"item of `resources` must be dict: {resource_config}"
            )
        import copy

        # upgrade resource config with template
        if template_id := resource_config.get("template"):
            template = self._get_template(template_id)
            resource_config = recursive_update(copy.deepcopy(template), resource_config)

        title = resource_config["title"]
        url = resource_config.get("url")
        enabled = resource_config.get("enabled", True)
        notifier_id = resource_config.get("notifier")
        notifier = self._get_notifier(notifier_id)
        env = resource_config.get("env")
        cmd = resource_config.get("cmd")

        if not ((url != None) ^ ((cmd or env) != None)):
            raise ConfigLoadError(
                f"we couldn't determine resource type: {resource_config}"
            )

        if url:
            return HttpResource(
                title=title,
                notifier=notifier,
                url=url,
                enabled=enabled,
            )
        elif cmd:
            return CommandResource(
                title=title,
                notifier=notifier,
                cmd=cmd,
                env=env or dict(),
                enabled=enabled,
            )
        else:
            raise NotImplementedError()

    def _get_template(self, template_id: str) -> Dict[str, Dict]:
        if self.templates:
            return self.templates[template_id]
        else:
            raise ConfigLoadError("You need to set `templates`")

    def _load_templates(self, templates_config: Dict[str, Dict]) -> Dict[str, Dict]:
        if not isinstance(templates_config, dict):
            raise ConfigLoadError(f"`templates` must be dict")
        templates = dict()
        for template_key, template_config in templates_config.items():
            templates[template_key] = template_config
        return templates
