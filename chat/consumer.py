import json
import requests
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings

import os

REDIS_URL = "redis://default:usBS4QJd1VkzdFlc3FAB2hWKV8nAUXIQ@redis-16662.c321.us-east-1-2.ec2.redns.redis-cloud.com:16662"
r = redis.Redis.from_url(REDIS_URL)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Mark user online
        user = self.scope["user"]
        if user.is_authenticated:
            await self.mark_user_online(user.id)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Mark user offline
        user = self.scope["user"]
        if user.is_authenticated:
            await self.mark_user_offline(user.id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        file = data.get('file')
        filename = data.get('filename')
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')

        msg_obj = await self.save_message(sender_id, receiver_id, message, file, filename)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_obj.text,
                'file': msg_obj.file_url() if hasattr(msg_obj, "file_url") else None,
                'filename': msg_obj.filename,
                'sender_id': msg_obj.sender.id,
                'receiver_id': msg_obj.receiver.id,
                'timestamp': msg_obj.timestamp.isoformat(),
            }
        )

        is_online = await self.is_user_online(receiver_id)
        if not is_online:
            await self.send_push_notification(receiver_id, message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event.get('message'),
            'file': event.get('file'),
            'filename': event.get('filename'),
            'sender_id': event.get('sender_id'),
            'receiver_id': event.get('receiver_id'),
            'timestamp': event.get('timestamp'),
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, text, file, filename):
        from django.contrib.auth import get_user_model
        from .models import Message
        User = get_user_model()
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        msg = Message.objects.create(
            sender=sender,
            receiver=receiver,
            text=text,
            filename=filename or "",
        )
        return msg

    @database_sync_to_async
    def mark_user_online(self, user_id):
        r.sadd("online_users", user_id)

    @database_sync_to_async
    def mark_user_offline(self, user_id):
        r.srem("online_users", user_id)

    @database_sync_to_async
    def is_user_online(self, user_id):
        return r.sismember("online_users", user_id)

    @database_sync_to_async
    def send_push_notification(self, user_id, message):
        from .models import Player
        try:
            player = Player.objects.get(user_id=user_id)
            headers = {
                "Authorization": f"Basic {settings.ONESIGNAL_REST_API_KEY}",
                "Content-Type": "application/json"
            }
    
            payload = {
                "app_id": settings.ONESIGNAL_APP_ID,
                "include_player_ids": [player.player_id],  # use player_id now
                "contents": {"en": message},
                "headings": {"en": "New Message"},
            }
    
            response = requests.post("https://api.onesignal.com/notifications", json=payload, headers=headers)
            print("Push response:", response.status_code, response.json())
    
        except Player.DoesNotExist:
            print(f"[OneSignal] No player ID for user {user_id}")
        except Exception as e:
            print("Push notification error:", e)
    
