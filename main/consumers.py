import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class FirstConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        await self.send(text_data="You said: " + text_data)