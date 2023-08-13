from django.shortcuts import render
from django.views import View
from django.utils.safestring import mark_safe
import json


class LobbyView(View):
    def get(self, request):
        return render(request, 'chat_app/lobby.html')


class RoomView(View):
    def get(self, request, room_name):
        username = request.user.username
        context = {
            'room_name': room_name,
            'username': mark_safe(json.dumps(username)),
            }
        return render(request, 'chat_app/room.html', context=context)
