class Notifier():
    def __init__(self, _id) -> None:
        self.id = _id

    def send(self, message: str):
        raise NotImplementedError()
