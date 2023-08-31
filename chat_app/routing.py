from django.urls import re_path
from .consumers import ChatConsumer, VideoChatConsumer

app_name = 'routing'
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi(), name='chat-consumer'),
    re_path(r"ws/videochat/", VideoChatConsumer.as_asgi(), name='VideoChat-consumer'),
]
