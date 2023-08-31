from datetime import datetime
from django.db import models
from django.utils.text import slugify
from account_app.models import User


class ChatRoom(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='room_creator')
    room_name = models.CharField(max_length=50, unique=True)
    members = models.ManyToManyField(User, related_name='rooms')
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


STATUS_LIST = {
    0: 'Contacting',
    1: 'Not Available',
    2: 'Accepted',
    3: 'Rejected',
    4: 'Busy',
    5: 'Processing',
    6: 'Ended',
}


class VideoCall(models.Model):
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caller')
    callee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='callee')
    status = models.PositiveSmallIntegerField(default=0)
    date_started = models.DateTimeField(default=datetime.now())
    date_ended = models.DateTimeField(default=datetime.now())
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def status_name(self):
        return STATUS_LIST[self.status]

    @property
    def duration(self):
        return self.date_ended - self.date_started
