from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id')
    receiver_id = serializers.IntegerField(source='receiver.id')
    message = serializers.CharField(source='text')  # <--- add this line

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'receiver_id', 'message', 'file', 'filename', 'timestamp']