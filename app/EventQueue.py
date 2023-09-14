import asyncio


class AsyncEventQueue:
    def __init__(self):
        self.q = asyncio.Queue()

    async def hasEvent(self) -> bool:
        return self.q.qsize() > 0

    async def send(self, data):
        await self.q.put(data)

    async def receive(self):
        return await self.q.get()

    async def __call__(self, data):
        await self.send(data)
