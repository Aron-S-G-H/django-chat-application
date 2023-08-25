from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
import json
from .models import ChatRoom
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class LobbyView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(members=user).prefetch_related('members').defer('members')
        return render(request, 'chat_app/lobby.html', {'chat_rooms': chat_rooms, 'user': user})

    def post(self, request):
        room_name = request.POST.get('room_name', None)
        user = request.user
        if room_name and user:
            try:
                chat_room = ChatRoom.objects.get(room_name=room_name)
                if user in chat_room.members.all():
                    return JsonResponse({'status': 409})
                else:
                    return JsonResponse({"status": 200})
            except ChatRoom.DoesNotExist:
                return JsonResponse({"status": 404})
        return JsonResponse({'status': 400})


class RoomView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request, room_slug):
        username = request.user.username
        chat_model = ChatRoom.objects.get(slug=room_slug)
        context = {
            'chat_model': chat_model,
            'room_name': chat_model.room_name,
            'username': mark_safe(json.dumps(username)),
        }
        return render(request, 'chat_app/room.html', context=context)


class CreateRoomView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def post(self, request):
        user = request.user
        room_name = request.POST.get('room_name', None)
        if not room_name:
            return JsonResponse({'status': 400})
        elif ChatRoom.objects.filter(room_name=room_name).exists():
            return JsonResponse({'status': 409})
        else:
            created_room = ChatRoom.objects.create(room_name=room_name, creator=user)
            created_room.members.add(user)
            return JsonResponse({'status': 200})


def join_room(request):
    if request.method == 'POST':
        user = request.user
        room_name = request.POST.get('room_name', None)
        if user and room_name:
            channel_layer = get_channel_layer()
            room_group_name = f'chat_{room_name}'
            async_to_sync(channel_layer.group_send)(
                room_group_name, {
                    'type': 'chat_message',
                    'command': 'info',
                    'content': json.dumps({'type': 'join', 'message': f'{user.username} joined the room'}),
                }
            )
            room = ChatRoom.objects.get(room_name=room_name)
            room.members.add(user)
            return JsonResponse({'status': 200})
    return JsonResponse({'status': 400})


def remove_room(request):
    room_name = request.GET.get('room_name', None)
    user = request.user
    room_group_name = f'chat_{room_name}'
    chat_room = ChatRoom.objects.get(room_name=room_name)
    if room_name and user:
        if user == chat_room.creator:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group_name, {
                    'type': 'chat_message',
                    'command': 'info',
                    'content': json.dumps({'type': 'delete', 'message': 'Creator delete the room'}),
                }
            )
            chat_room.delete()
        else:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group_name, {
                    'type': 'chat_message',
                    'command': 'info',
                    'content': json.dumps({'type': 'left', 'message': f'{user.username} left the room'}),
                }
            )
            chat_room.members.remove(user)
        return JsonResponse({'status': 200})
    return JsonResponse({'status': 400})
