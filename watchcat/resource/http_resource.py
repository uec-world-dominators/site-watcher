import requests
from watchcat.notifier.notifier import Notifier
from watchcat.resource.errors import GetError
from watchcat.resource.resource import Resource


class HttpResource(Resource):
    def __init__(
        self,
        title: str,
        notifier: Notifier,
        url: str,
        enabled: bool = True,
    ):
        """init

        Parameters
        ----------
        title : str
            タイトル
        notifier : Notifier
            通知元
        url : str
            URL
        enabled : bool, optional
            有効かどうか, by default True
        """
        super().__init__(title, notifier, enabled)
        self.url = url

    def get(self):
        """url先のhtmlテキストを取得

        Returns
        -------
        str
            htmlテキスト

        Raises
        ------
        GetError
            取得エラー
        """
        response = requests.get(self.url)
        if response.status_code == 200:
            text = response.text
            return text
        else:
            raise GetError()
