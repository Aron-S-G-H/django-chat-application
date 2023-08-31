from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
import json
from .models import ChatRoom, Message, VideoCall
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required


class LobbyView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(members=user).prefetch_related('members')
        return render(request, 'chat_app/lobby.html', {'chat_rooms': chat_rooms})

    def post(self, request):
        # post method for checking room existence and user - used for search room feature
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
        try:
            chat_model = ChatRoom.objects.get(slug=room_slug)
            message_model = Message.objects.filter(chat_room=chat_model).select_related('chat_room', 'author')
            context = {
                'message_model': message_model,
                'chat_model': chat_model,
                'room_name': chat_model.room_name,
                'username': mark_safe(json.dumps(username)),
            }
            return render(request, 'chat_app/room.html', context=context)
        except ChatRoom.DoesNotExist:
            raise ValidationError('Room does not exist, Maybe it was deleted by its creator')


@login_required(login_url='account:login')
@csrf_protect
def create_room_view(request):
    if request.method == 'POST':
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


@login_required(login_url='account:login')
@csrf_protect
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
                    'content': {
                        'type': 'join',
                        'message': f'{user.username} joined the room',
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'username': user.username,
                    },
                }
            )
            room = ChatRoom.objects.get(room_name=room_name)
            room.members.add(user)
            return JsonResponse({'status': 200})
    return JsonResponse({'status': 400})


@login_required(login_url='account:login')
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
                    'content': {'type': 'delete', 'message': 'Creator delete the room'},
                }
            )
            chat_room.delete()
        else:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group_name, {
                    'type': 'chat_message',
                    'command': 'info',
                    'content': {
                        'type': 'left',
                        'message': f'{user.username} left the room',
                        'username': user.username,
                    },
                }
            )
            chat_room.members.remove(user)
        return JsonResponse({'status': 200})
    return JsonResponse({'status': 400})


@login_required(login_url='account:login')
def video_call(request, room_slug):
    user = request.user
    chat_room_name = ChatRoom.objects.get(slug=room_slug).room_name
    call_logs = VideoCall.objects.filter(Q(callee_id=user.id) | Q(caller_id=user.id)).order_by('-date_created')[:5]
    return render(request, 'chat_app/video_call.html', {
        'call_logs': call_logs,
        'room_name': mark_safe(json.dumps(chat_room_name)),
    })
