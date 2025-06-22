from rest_framework import serializers
from .models import Message
from .models import OneSignal
from user.models import CustomUser
class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id')
    receiver_id = serializers.IntegerField(source='receiver.id')
    message = serializers.CharField(source='text')  # <--- add this line

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'receiver_id', 'message', 'file', 'filename', 'timestamp']


class OneSignalSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OneSignal
        fields = ['user_id', 'player_id']

    def validate_user_id(self, value):
        try:
             CustomUser.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = CustomUser.objects.get(id=user_id)
        onesignal, created = OneSignal.objects.update_or_create(
            user=user,
            defaults={'player_id': validated_data['player_id']}
        )
        return onesignal
