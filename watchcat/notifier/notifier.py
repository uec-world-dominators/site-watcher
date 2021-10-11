class Notifier():
    def __init__(self) -> None:
        self.id = None

    def send(self, message: str):
        raise NotImplementedError()
