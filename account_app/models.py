from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


class User(AbstractUser):
    email = models.EmailField(unique=True, null=True)
    profile_picture = models.ImageField(upload_to='user-profile', null=True, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


# OTP = ONE TIME PASSWORD
class Otp(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=60)
    code = models.SmallIntegerField()
    token = models.CharField(max_length=125)

    def __str__(self):
        return self.username
