import sys
import time
from typing import Union

import requests
from requests.auth import AuthBase
from watchcat.notifier.notifier import Notifier
from watchcat.resource.errors import GetError
from watchcat.resource.resource import Resource
from watchcat.snapshot import Snapshot


class HttpResource(Resource):
    def __init__(
        self,
        resource_id: str,
        notifier: Notifier,
        url: str,
        enabled: bool = True,
        title: Union[str, None] = None,
        auth: AuthBase = None,
    ):
        """init

        Parameters
        ----------
        resource_id : str
            一意なid
        notifier : Notifier
            通知元
        url : str
            URL
        enabled : bool, optional
            有効かどうか, by default True
        title : Union[str, None], optional
            通知に表示されるタイトル, by default None
        auth : requests.auth.AuthBase
            認証情報
        """
        super().__init__(resource_id, notifier, enabled, title or url)
        self.url = url
        self.auth = auth

    def get(self) -> Snapshot:
        """url先のhtmlテキストを取得

        Returns
        -------
        Snapshot
            スナップショット

        Raises
        ------
        GetError
            取得エラー
        """
        response = requests.get(self.url, auth=self.auth)
        if response.status_code == 200:
            text = response.text
            timestamp = time.time()
            snapshot = Snapshot(self.resource_id, timestamp, text)
            return snapshot
        else:
            print(response.status_code, file=sys.stderr)
            print(response.text, file=sys.stderr)
            raise GetError()
