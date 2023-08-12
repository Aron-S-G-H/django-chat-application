from django.urls import path
from . import views


app_name = 'chat'
urlpatterns = [
    path('chat/lobby', views.LobbyView.as_view(), name='lobby'),
    path('chat/room/<str:room_name>', views.RoomView.as_view(), name='room'),
]
