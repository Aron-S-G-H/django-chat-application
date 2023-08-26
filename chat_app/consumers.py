from rest_framework.renderers import JSONRenderer
from channels.db import database_sync_to_async
from account_app.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .serializer import MessageSerializer, ChatRoomSerializer
import base64
from django.core.files.base import ContentFile
from.models import Message, ChatRoom


def image_fixer(image_data):
    format, imgstr = image_data.split(';base64,')
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr), name='image')
    return data


def new_message_query(username, room_name, message=None, image=None):
    user = User.objects.get(username=username)
    chat_room = ChatRoom.objects.get(room_name=room_name)
    massage_model = Message.objects.create(author=user, content=message, chat_room=chat_room)
    if image:
        data = image_fixer(image)
        massage_model.image.save('image.jpg', data)
        massage_model.save()
    return massage_model


def room_icon_query(room_name, image_data):
    chat_room = ChatRoom.objects.get(room_name=room_name)
    image = image_fixer(image_data)
    chat_room.room_image.save('image.jpg', image)
    chat_room.save()
    return chat_room


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope['user']

        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
        else:
            await self.disconnect(403)

    async def new_message(self, data):
        message = data.get('message', None)
        image = data.get('image', None)
        username = data.get('username', None)
        room_name = data.get('roomName', None)
        create_new_message = await database_sync_to_async(new_message_query)(username, room_name, message, image)
        new_message_json = await self.message_serializer(create_new_message)
        result = eval(new_message_json)  # REMOVE BYTE STRING
        if image:
            context = {'command': 'image', 'result': result}
        else:
            context = {'command': 'new_message', 'result': result}
        await self.send_to_chat_message(context)

    async def change_icon(self, data):
        username = data.get('username', None)
        room_name = data.get('roomName', None)
        image_data = data.get('image', None)
        change_room_icon = await database_sync_to_async(room_icon_query)(room_name, image_data)
        room_icon_json = await self.room_icon_serializer(change_room_icon)
        result = eval(room_icon_json)
        context = {'command': 'change_icon', 'result': result}
        await self.send_to_chat_message(context)
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'command': 'info',
            'content': {'type': 'changeIcon', 'message': f'{username} changed the room icon'},
        })


    async def message_serializer(self, query):
        serialized_message = MessageSerializer(query)
        message_json = JSONRenderer().render(serialized_message.data)
        return message_json

    async def room_icon_serializer(self, query):
        serialize_icon = ChatRoomSerializer(query)
        icon_json = JSONRenderer().render(serialize_icon.data)
        return icon_json

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_dict = json.loads(text_data)
            command = text_data_dict['command']
            await self.commands[command](self, text_data_dict)

    async def send_to_chat_message(self, data):
        command = data.get('command')
        if command == 'image' or command == 'new_message':
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "chat_message",
                "content": (lambda content: data['result']['image'] if(command == 'image') else data['result']['content'])(command),
                "__str__": data['result']['__str__'],
                "created_at": data['result']['created_at'],
                'command': command,
            })
        elif command == 'change_icon':
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'content': data['result']['room_image'],
                'command': command,
            })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    commands = {
        'new_message': new_message,
        'change_icon': change_icon,
    }

