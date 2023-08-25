from django.urls import path
from . import views


app_name = 'chat'
urlpatterns = [
    path('lobby', views.LobbyView.as_view(), name='lobby'),
    path('room/<slug:room_slug>', views.RoomView.as_view(), name='room'),
    path('create', views.create_room_view, name='create-room'),
    path('join-room', views.join_room, name='join-room'),
    path('remove-room', views.remove_room, name='remove-room'),
]
