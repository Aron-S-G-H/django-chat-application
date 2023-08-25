from django.db import models
from django.utils.text import slugify

from account_app.models import User


class ChatRoom(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='room_creator')
    room_name = models.CharField(max_length=50, unique=True)
    members = models.ManyToManyField(User, related_name='members')
    room_image = models.ImageField(upload_to='room-image', blank=True, null=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.room_name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.room_name)
        super(ChatRoom, self).save()


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(blank=True,  null=True, upload_to='image-message')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username
