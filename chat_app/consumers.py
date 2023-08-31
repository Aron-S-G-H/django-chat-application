from channels.exceptions import StopConsumer
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from channels.db import database_sync_to_async
from account_app.models import User
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer
import json
from .serializer import MessageSerializer, ChatRoomSerializer
import base64
from django.core.files.base import ContentFile
from .models import Message, ChatRoom, VideoCall
from datetime import datetime


def image_fixer(image_data):
    format, imgstr = image_data.split(';base64,')
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr), name='image')
    return data


@database_sync_to_async
def new_message_query(username, room_name, message=None, image=None):
    user = User.objects.get(username=username)
    chat_room = ChatRoom.objects.get(room_name=room_name)
    massage_model = Message.objects.create(author=user, content=message, chat_room=chat_room)
    if image:
        data = image_fixer(image)
        massage_model.image.save('image.jpg', data)
        massage_model.save()
    return massage_model


@database_sync_to_async
def room_icon_query(room_name, image_data):
    chat_room = ChatRoom.objects.get(room_name=room_name)
    image = image_fixer(image_data)
    chat_room.room_image.save('image.jpg', image)
    chat_room.save()
    return chat_room


@database_sync_to_async
def clear_history_query(room_name):
    try:
        chat_room_messages = Message.objects.filter(chat_room__room_name=room_name)
        chat_room_messages.delete()
        return True
    except:
        return False


@database_sync_to_async
def get_chat_room(room_name):
    return ChatRoom.objects.get(room_name=room_name)


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
        await self.notification(data)
        message = data.get('message', None)
        image = data.get('image', None)
        username = data.get('username', None)
        room_name = data.get('roomName', None)
        create_new_message = await new_message_query(username, room_name, message, image)
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
        change_room_icon = await room_icon_query(room_name, image_data)
        room_icon_json = await self.room_icon_serializer(change_room_icon)
        result = eval(room_icon_json)
        context = {'command': 'change_icon', 'result': result}
        await self.send_to_chat_message(context)
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'command': 'info',
            'content': {'type': 'changeIcon', 'message': f'{username} changed the room icon'},
        })

    async def clear_history(self, data):
        room_name = data.get('roomName', None)
        clear_history = await clear_history_query(room_name)
        if clear_history:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'command': 'clear_history',
            })

    async def notification(self, data):
        room_name = data['roomName']
        username = data['username']
        message = data.get('message', None)
        image = data.get('image', None)
        members_list = []
        chat_room = await get_chat_room(room_name)
        for _ in chat_room.members.all():
            members_list.append(_.username)

        result = {
            'type': 'chat_message',
            'content': 'message',
            '__str__': username,
            'room_name': room_name,
            'members_list': members_list,
        }
        if image:
            result['content'] = 'image'

        await self.channel_layer.group_send('chat_listener', result)

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
                "content": (
                    lambda content: data['result']['image'] if (command == 'image') else data['result']['content'])(
                    command),
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
        'clear_history': clear_history,
    }


# Video Call Status
VC_CONTACTING, VC_NOT_AVAILABLE, VC_ACCEPTED, VC_REJECTED, VC_BUSY, VC_PROCESSING, VC_ENDED = \
    0, 1, 2, 3, 4, 5, 6


class VideoChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.user = self.scope['user']
        self.user_room_id = f"videochat_{self.user.id}"

        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.user_room_id,
                self.channel_name
            )

            await self.send({
                'type': 'websocket.accept'
            })
        else:
            await self.websocket_disconnect()

    async def websocket_disconnect(self):
        video_thread_id = self.scope['session'].get('video_thread_id', None)
        videothread = await self.change_videothread_status(video_thread_id, VC_ENDED)
        if videothread is not None:
            await self.change_videothread_datetime(video_thread_id, False)
            await self.channel_layer.group_send(
                f"videochat_{videothread.caller.id}",
                {
                    'type': 'chat_message',
                    'message': json.dumps(
                        {'type': "offerResult", 'status': VC_ENDED, 'video_thread_id': videothread.id}),
                }
            )
            await self.channel_layer.group_send(
                f"videochat_{videothread.callee.id}",
                {
                    'type': 'chat_message',
                    'message': json.dumps(
                        {'type': "offerResult", 'status': VC_ENDED, 'video_thread_id': videothread.id}),
                }
            )
        await self.channel_layer.group_discard(
            self.user_room_id,
            self.channel_name
        )
        raise StopConsumer()

    async def websocket_receive(self, event):
        text_data = event.get('text', None)

        if text_data:
            text_data_json = json.loads(text_data)
            message_type = text_data_json['type']

            if message_type == "createOffer":
                callee_username = text_data_json['username']
                room_name = text_data_json['room_name']
                status, video_thread_id = await self.create_videothread(callee_username, room_name)

                await self.send({
                    'type': 'websocket.send',
                    'text': json.dumps({'type': "offerResult", 'status': status, 'video_thread_id': video_thread_id})
                })

                if status == VC_CONTACTING:
                    videothread = await self.get_videothread(video_thread_id)

                    await self.channel_layer.group_send(
                        f"videochat_{videothread.callee.id}",
                        {
                            'type': 'chat_message',
                            'message': json.dumps(
                                {'type': "offer", 'username': self.user.username, 'video_thread_id': video_thread_id}),
                        }
                    )

            elif message_type == "cancelOffer":
                video_thread_id = text_data_json['video_thread_id']
                videothread = await self.get_videothread(video_thread_id)
                self.scope['session']['video_thread_id'] = None
                self.scope['session'].save()

                if videothread.status != VC_ACCEPTED or videothread.status != VC_REJECTED:
                    await self.change_videothread_status(video_thread_id, VC_NOT_AVAILABLE)
                    await self.send({
                        'type': 'websocket.send',
                        'text': json.dumps(
                            {'type': "offerResult", 'status': VC_NOT_AVAILABLE, 'video_thread_id': videothread.id})
                    })
                    await self.channel_layer.group_send(
                        f"videochat_{videothread.callee.id}",
                        {
                            'type': 'chat_message',
                            'message': json.dumps({'type': "offerFinished"}),
                        }
                    )

            elif message_type == "acceptOffer":
                video_thread_id = text_data_json['video_thread_id']
                videothread = await self.change_videothread_status(video_thread_id, VC_PROCESSING)
                await self.change_videothread_datetime(video_thread_id, True)

                await self.channel_layer.group_send(
                    f"videochat_{videothread.caller.id}",
                    {
                        'type': 'chat_message',
                        'message': json.dumps(
                            {'type': "offerResult", 'status': VC_ACCEPTED, 'video_thread_id': videothread.id}),
                    }
                )

            elif message_type == "rejectOffer":
                video_thread_id = text_data_json['video_thread_id']
                videothread = await self.change_videothread_status(video_thread_id, VC_REJECTED)
                self.scope['session']['video_thread_id'] = None
                self.scope['session'].save()

                await self.channel_layer.group_send(
                    f"videochat_{videothread.caller.id}",
                    {
                        'type': 'chat_message',
                        'message': json.dumps(
                            {'type': "offerResult", 'status': VC_REJECTED, 'video_thread_id': videothread.id}),
                    }
                )

            elif message_type == "hangUp":
                video_thread_id = text_data_json['video_thread_id']
                videothread = await self.change_videothread_status(video_thread_id, VC_ENDED)
                await self.change_videothread_datetime(video_thread_id, False)
                self.scope['session']['video_thread_id'] = None
                self.scope['session'].save()

                await self.channel_layer.group_send(
                    f"videochat_{videothread.caller.id}",
                    {
                        'type': 'chat_message',
                        'message': json.dumps(
                            {'type': "offerResult", 'status': VC_ENDED, 'video_thread_id': videothread.id}),
                    }
                )
                await self.channel_layer.group_send(
                    f"videochat_{videothread.callee.id}",
                    {
                        'type': 'chat_message',
                        'message': json.dumps(
                            {'type': "offerResult", 'status': VC_ENDED, 'video_thread_id': videothread.id}),
                    }
                )

            elif message_type == "callerData":
                video_thread_id = text_data_json['video_thread_id']
                videothread = await self.get_videothread(video_thread_id)

                await self.channel_layer.group_send(
                    f"videochat_{videothread.callee.id}",
                    {
                        'type': 'chat_message',
                        'message': text_data,
                    }
                )

            elif message_type == "calleeData":
                video_thread_id = text_data_json['video_thread_id']
                videothread = await self.get_videothread(video_thread_id)

                await self.channel_layer.group_send(
                    f"videochat_{videothread.caller.id}",
                    {
                        'type': 'chat_message',
                        'message': text_data,
                    }
                )

    async def chat_message(self, event):
        message = event['message']

        await self.send({
            'type': 'websocket.send',
            'text': message
        })

    @database_sync_to_async
    def get_videothread(self, id):
        try:
            videothread = VideoCall.objects.get(id=id)
            return videothread
        except VideoCall.DoesNotExist:
            return None

    @database_sync_to_async
    def create_videothread(self, callee_username, room_name):
        try:
            callee = User.objects.get(username=callee_username)
            if not callee.rooms.filter(room_name=room_name).exists():
                return 404, None
        except User.DoesNotExist:
            return 404, None

        if VideoCall.objects.filter(Q(caller_id=callee.id) | Q(callee_id=callee.id), status=VC_PROCESSING).exists():
            return VC_BUSY, None

        videothread = VideoCall.objects.create(caller_id=self.user.id, callee_id=callee.id)
        self.scope['session']['video_thread_id'] = videothread.id
        self.scope['session'].save()

        return VC_CONTACTING, videothread.id

    @database_sync_to_async
    def change_videothread_status(self, id, status):
        try:
            videothread = VideoCall.objects.get(id=id)
            videothread.status = status
            videothread.save()
            return videothread
        except VideoCall.DoesNotExist:
            return None

    @database_sync_to_async
    def change_videothread_datetime(self, id, is_start):
        try:
            videothread = VideoCall.objects.get(id=id)
            if is_start:
                videothread.date_started = datetime.now()
            else:
                videothread.date_ended = datetime.now()
            videothread.save()
            return videothread
        except VideoCall.DoesNotExist:
            return None


    
