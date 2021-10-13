import subprocess
from typing import Dict

from watchcat.notifier.notifier import Notifier
from watchcat.resource.errors import GetError
from watchcat.resource.resource import Resource


class CommandResource(Resource):
    def __init__(
        self,
        title: str,
        notifier: Notifier,
        cmd: str,
        env: Dict[str, str] = dict(),
        enabled: bool = True,
    ):
        """init

        Parameters
        ----------
        title : str
            タイトル
        notifier : Notifier
            通知元
        cmd : str
            実行コマンド
        env : Dict[str, str], optional
            環境変数, by default dict()
        enabled : bool, optional
            実行するかどうか, by default True
        """
        super().__init__(title, notifier, enabled=enabled)
        self.title = title
        self.notifier = notifier
        self.cmd = cmd
        self.env = env

    def get(self):
        """コマンドを実行して返り値を取得

        Returns
        -------
        str
            テキスト

        Raises
        ------
        GetError
            取得エラー
        """
        response = subprocess.run(self.cmd, shell=True, env=self.env, stdout=subprocess.PIPE)
        if response.returncode == 0:
            text = response.stdout.decode(encoding="utf-8")
            return text
        else:
            raise GetError()
