from django.contrib import admin
from .models import Message, ChatRoom, VideoCall


admin.site.register(Message)
admin.site.register(ChatRoom)
admin.site.register(VideoCall)
