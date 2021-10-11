from watchcat.notifier.notifier import Notifier


class Resource:
    def __init__(self, title: str, notifier: Notifier, enabled: bool = True):
        """init

        Parameters
        ----------
        title : str
            タイトル
        notifier : Notifier
            通知元
        enabled : bool, optional
            通知するかどうか, by default True
        """
        self.title = title
        self.notifier = notifier
        self.enabled = enabled

    def get():
        raise NotImplementedError()
