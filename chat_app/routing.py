from django.urls import re_path
from .consumers import ChatConsumer

app_name = 'routing'
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi(), name='chat-consumer'),
]
