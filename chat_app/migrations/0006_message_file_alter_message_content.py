# Generated by Django 4.2.4 on 2023-08-21 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0005_remove_chatroom_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='image-message'),
        ),
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
