from typing import Union

from watchcat.notifier.notifier import Notifier


class Resource:
    def __init__(self, resource_id: str, notifier: Notifier, enabled: bool = True, title: Union[str, None] = None):
        """init

        Parameters
        ----------
        resource_id : str
            一意なid
        notifier : Notifier
            通知元
        enabled : bool, optional
            通知するかどうか, by default True
        title : Union[str, None], optional
            通知に表示されるタイトル, by default None
        """
        self.resource_id = resource_id
        self.notifier = notifier
        self.enabled = enabled
        self.title = title

    def get(self):
        raise NotImplementedError()
