# Generated by Django 4.2.4 on 2023-08-16 21:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat_app', '0003_message_chat_room'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(allow_unicode=True, unique=True)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='message',
            name='chat_room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chat_app.chatroom'),
        ),
        migrations.DeleteModel(
            name='Chat',
        ),
    ]