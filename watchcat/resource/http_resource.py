import requests
from watchcat.resource.errors import GetError
from watchcat.resource.resource import Resource


class HttpResource(Resource):
    def __init__(
        self, title: str, url: str, enabled: bool = True,
    ):
        """init

        Parameters
        ----------
        title : str
            タイトル
        url : str
            URL
        """
        super().__init__(title, enabled=enabled)
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
