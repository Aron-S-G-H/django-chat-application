from django.shortcuts import render
from django.views import View


class LobbyView(View):
    def get(self, request):
        return render(request, 'chat_app/lobby.html')


class RoomView(View):
    def get(self, request, room_name):
        context = {'room_name': room_name}
        return render(request, 'chat_app/room.html', context=context)
