from rest_framework.renderers import JSONRenderer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .serializer import MessageSerializer
from.models import Message


def get_message_query():
    return Message.objects.order_by('-created_at').select_related('author')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def new_message(self):
        print('salam')

    async def fetch_message(self):
        message_query = await database_sync_to_async(get_message_query)()
        message_json = await self.meessage_serializer(message_query)
        content = {
            'message': eval(message_json)
        }
        await self.chat_message(content)

    async def meessage_serializer(self, query_set):
        serialized_message = MessageSerializer(query_set, many=True)
        message_json = JSONRenderer().render(serialized_message.data)
        return message_json

    async def disconnect(self, code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_dict = json.loads(text_data)
            message = text_data_dict.get('message', None)
            command = text_data_dict['command']

            await self.commands[command](self)

    async def send_to_chat_message(self, message):
        # Send message to room group
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "chat_message",
            "message": message
        })

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            'message': message,
        }))

    commands = {
        'new_message': new_message,
        'fetch_message': fetch_message,
    }

