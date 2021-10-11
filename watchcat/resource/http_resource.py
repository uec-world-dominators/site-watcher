import requests
from watchcat.resource.errors import GetError
from watchcat.resource.resource import Resource


class HttpResource(Resource):
    def __init__(
        self, title: str, url: str,
    ):
        """init

        Parameters
        ----------
        title : str
            サイト名
        url : str
            URL
        """
        self.title = title
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
