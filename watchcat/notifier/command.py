import subprocess

from .notifier import Notifier


class CommandNotifier(Notifier):
    def __init__(self, _id: str, command: str) -> None:
        super().__init__(_id)
        self.command = command

    def send(self, message: str):
        process = subprocess.run(self.command, shell=True, check=True, env={"message": message})
        return process.returncode

    def __repr__(self) -> str:
        return f"<CommandNotifier(command={self.command})>"
