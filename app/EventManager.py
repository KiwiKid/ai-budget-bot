class EventManager:
    def __init__(self):
        self._subscribers = set()

    def subscribe(self, subscriber):
        self._subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        self._subscribers.remove(subscriber)

    def notify(self, event: str, message: str):
        data = {"event": event, "message": message}
        print(f"notify notify notify notify {data}")
        for subscriber in list(self._subscribers):
            subscriber(data)  # since subscriber is now callable
