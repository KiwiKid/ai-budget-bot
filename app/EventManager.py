import json


class EventManager:
    def __init__(self):
        self._subscribers = set()

    async def subscribe(self, subscriber):
        self._subscribers.add(subscriber)

    async def unsubscribe(self, subscriber):
        if subscriber in self._subscribers:  # Add a check to prevent KeyErrors
            self._subscribers.remove(subscriber)

    async def notify(self, event, payload):
        # Convert the event data to a JSON string
        json_event = json.dumps({'event': event, 'payload': payload})
        formatted_event = f"data: {json_event}\n\n"

        for subscriber in list(self._subscribers):
            print(f"notify notify notify notify {formatted_event}")
            # since subscriber is now callable
            await subscriber(formatted_event)
