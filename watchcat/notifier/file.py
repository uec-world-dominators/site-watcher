from .notifier import Notifier


class FileNotifier(Notifier):
    def __init__(self, _id, path: str) -> None:
        super().__init__(_id)
        self.path = path

    def send(self, message: str):
        with open(self.path, "wt", encoding="utf-8") as f:
            f.write(message + "\n")

    def __str__(self) -> str:
        return f"<FileNotifier(path={self.path})>"
