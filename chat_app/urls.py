from django.urls import path
from . import views


app_name = 'chat'
urlpatterns = [
    path('lobby', views.LobbyView.as_view(), name='lobby'),
    path('room/<str:room_name>', views.RoomView.as_view(), name='room'),
    path('create', views.CreateRoomView.as_view(), name='create-room'),
    path('join-room', views.join_room, name='join-room'),
]
