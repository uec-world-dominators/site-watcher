import subprocess
from .notifier import Notifier


class CommandNotifier(Notifier):
    def __init__(self, command: str) -> None:
        self.command = command

    def send(self, message: str):
        process = subprocess.run(
            self.command,
            shell=True,
            check=True,
            env={
                "message": message,
            },
        )
        return process.returncode
