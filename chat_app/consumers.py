from rest_framework.renderers import JSONRenderer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .serializer import MessageSerializer
from.models import Message


def fetch_message_query():
    return Message.objects.order_by('created_at').select_related('author')


def new_message_query(username, message):
    user = User.objects.get(username=username)
    return Message.objects.create(author=user, content=message)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def new_message(self, data):
        message = data.get('message', None)
        username = data.get('username', None)
        create_new_message = await database_sync_to_async(new_message_query)(username, message)
        new_message_json = await self.message_serializer(create_new_message)
        result = eval(new_message_json)
        await self.send_to_chat_message(result)

    async def fetch_message(self):
        message_query = await database_sync_to_async(fetch_message_query)()
        message_json = await self.message_serializer(message_query)
        content = {
            'message': eval(message_json),
            'command': 'fetch_message',
        }
        await self.chat_message(content)

    async def message_serializer(self, query):
        serialized_message = MessageSerializer(query, many=(lambda query: True if (query.__class__.__name__ == 'QuerySet') else False)(query))
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
            command = text_data_dict['command']
            if command == 'fetch_message':
                await self.commands[command](self)
            else:
                await self.commands[command](self, text_data_dict)

    async def send_to_chat_message(self, data):
        # Send message to room group
        print(data)
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "chat_message",
            "content": data['content'],
            "__str__": data['__str__'],
            'command': 'new_message'
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    commands = {
        'new_message': new_message,
        'fetch_message': fetch_message,
    }

