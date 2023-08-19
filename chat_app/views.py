from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
import json
from .models import ChatRoom


class LobbyView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(members=user).prefetch_related('members').defer('members')
        return render(request, 'chat_app/lobby.html', {'chat_rooms': chat_rooms, 'user': user})

    def post(self, request):
        room_name = request.POST.get('room_name')
        user = request.user
        chat_room = ChatRoom.objects.filter(room_name=room_name).prefetch_related('members')
        if chat_room.exists():
            if user not in chat_room[0].members.all:
                chat_room[0].members.add(user)
            return render(request, 'chat_app/lobby.html', {'chat_rooms': chat_room, 'user': user})
        else:
            return render(request, 'chat_app/lobby.html', {'user': user})


class RoomView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request, room_name):
        username = request.user.username
        context = {
            'room_name': room_name,
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
            created_room = ChatRoom.objects.create(room_name=room_name)
            created_room.members.add(user)
            return JsonResponse({'status': 200})



