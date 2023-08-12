from django.db import models
from django.contrib.auth import get_user_model


user = get_user_model()


class Message(models.Model):
    author = models.ForeignKey(user, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
