import datetime
import json
import os
import time

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "text_to_img.settings")

# Get the ASGI application for Django
django_asgi_app = get_asgi_application()

from channels.generic.websocket import AsyncWebsocketConsumer

from user.models import ChatRoom, ChatMessage, CustomUser


class NewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def save_chat_message(self, room_name, user, message):
        room = ChatRoom.objects.get(name=room_name)
        ChatMessage.objects.create(room=room, user=user, content=message)

    @sync_to_async
    def get_user_by_id(self, user_id):
        User = CustomUser
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = text_data_json["user_id"]

        # Retrieve the user instance based on the user_id
        user = await self.get_user_by_id(user_id)
        print(user)

        if user:
            # Save the message to the database using the retrieved user instance
            await self.save_chat_message(self.room_name, user, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message,
                    'user_id': user.id,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
        }))