from django.contrib import admin
from .models import Message, ChatRoom


class ChatRoomAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('room_name',)}


admin.site.register(Message)
admin.site.register(ChatRoom, ChatRoomAdmin)
