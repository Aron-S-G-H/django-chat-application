from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
import json
from .models import Chat


class LobbyView(View):
    def get(self, request):
        chat_rooms = Chat.objects.filter(members=request.user).prefetch_related('members').defer('members')
        print(chat_rooms)
        return render(request, 'chat_app/lobby.html', {'chat_romms': chat_rooms})


class RoomView(View):
    def get(self, request, room_name):
        username = request.user.username
        context = {
            'room_name': room_name,
            'username': mark_safe(json.dumps(username)),
            }
        return render(request, 'chat_app/room.html', context=context)
