from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    room_name = models.CharField(max_length=50)
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.room_name


class Message(models.Model):
    chat_room = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username
