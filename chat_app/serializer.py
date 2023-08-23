from rest_framework import serializers
from .models import Message
from collections import OrderedDict


class MessageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(allow_null=True)

    def to_representation(self, instance):
        result = super(MessageSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])

    class Meta:
        model = Message
        fields = ['__str__', 'content', 'image', 'created_at']
