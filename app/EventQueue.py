import queue


class EventQueue:
    def __init__(self):
        self.q = queue.Queue()

    def send(self, data):
        self.q.put(data)

    def receive(self):
        return self.q.get()

    # This makes an instance of the class callable.
    def __call__(self, data):
        self.send(data)
