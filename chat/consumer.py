import json
import redis
import base64
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.files.base import ContentFile
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
        file_data = data.get('file')  # Base64 encoded file content
        filename = data.get('filename')
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')

        msg_obj = await self.save_message(sender_id, receiver_id, message, file_data, filename)

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
            sender = await self.get_user(sender_id)
            await self.send_push_notification(receiver_id, message, sender.username)

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
    def save_message(self, sender_id, receiver_id, text, file_data, filename):
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
        if file_data and filename:
            # Decode base64 file data and save it
            try:
                file_content = base64.b64decode(file_data)
                msg.file.save(filename, ContentFile(file_content))
                msg.save()
            except Exception as e:
                print(f"Error saving file: {e}")
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
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_player_id(self, user_id):
        from .models import OneSignal
        try:
            onesignal = OneSignal.objects.get(user_id=user_id)
            return onesignal.player_id
        except OneSignal.DoesNotExist:
            return None

    async def send_push_notification(self, receiver_id, message, sender_username):
        player_id = await self.get_player_id(receiver_id)
        if not player_id:
            print(f"[OneSignal] No player ID found for user {receiver_id}")
            return

        onesignal_app_id = "5f7fb217-caf4-4e0e-9aa6-28e73ef970f9"
        onesignal_api_key = "os_v2_app_l573ef6k6rha5gvgfdtt56lq7fmfpcp4wi5et5evzfzvraoabjb3anlfaovw76ljosc7ywwqqslko6c4zwp4snmmnbylchb57rlcyka"

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {onesignal_api_key}",
        }

        payload = {
            "app_id": onesignal_app_id,
            "include_player_ids": [player_id],
            "contents": {"en": f"{sender_username}: {message[:100]}"},
            "headings": {"en": f"New Message from {sender_username}"},
            "data": {"receiver_id": receiver_id, "sender_id": self.scope["user"].id},
        }

        try:
            response = requests.post(
                "https://onesignal.com/api/v1/notifications",
                headers=headers,
                data=json.dumps(payload),
            )
            print(f"[OneSignal] Notification sent to player {player_id}: Status {response.status_code}, Response {response.json()}")
        except Exception as e:
            print(f"[OneSignal] Error sending notification to player {player_id}: {e}")
