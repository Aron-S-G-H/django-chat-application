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


class RoomView(View):
    def get(self, request, room_name):
        username = request.user.username
        context = {
            'room_name': room_name,
            'username': mark_safe(json.dumps(username)),
        }
        return render(request, 'chat_app/room.html', context=context)
