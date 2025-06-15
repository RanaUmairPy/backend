# consumers.py
import json
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

# Track online users (in-memory, or replace with Redis)
online_users = {}

def add_user(room, user_id):
    if room not in online_users:
        online_users[room] = set()
    online_users[room].add(user_id)

def remove_user(room, user_id):
    if room in online_users:
        online_users[room].discard(user_id)

def is_user_online(room, user_id):
    return user_id in online_users.get(room, set())

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        add_user(self.room_name, self.user.id)

    async def disconnect(self, close_code):
        remove_user(self.room_name, self.user.id)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        file = data.get('file')
        filename = data.get('filename')
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        player_id = data.get('player_id')

        msg_obj = await self.save_message(sender_id, receiver_id, message, file, filename)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_obj.text,
                'file': msg_obj.file_url(),
                'filename': msg_obj.filename,
                'sender_id': msg_obj.sender.id,
                'receiver_id': msg_obj.receiver.id,
                'timestamp': msg_obj.timestamp.isoformat(),
            }
        )

        # Notify via OneSignal if offline
        if not is_user_online(self.room_name, receiver_id):
            await self.send_onesignal(player_id, f"New message", message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'file': event['file'],
            'filename': event['filename'],
            'sender_id': event['sender_id'],
            'receiver_id': event['receiver_id'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, text, file, filename):
        sender = get_user_model().objects.get(id=sender_id)
        receiver = get_user_model().objects.get(id=receiver_id)
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            text=text,
            filename=filename or "",
        )

    @database_sync_to_async
    def send_onesignal(self, player_id, title, body):
        headers = {
            "Authorization": "os_v2_app_l573ef6k6rha5gvgfdtt56lq7fmfpcp4wi5et5evzfzvraoabjbw2tv2hkgdesb7mthwqnvyuf544iqkeke4mvnbqm2i43bicutz3gi",
            "Content-Type": "application/json"
        }
        payload = {
            "app_id": "5f7fb217-caf4-4e0e-9aa6-28e73ef970f9",
            "include_player_ids": [player_id],
            "headings": {"en": title},
            "contents": {"en": body},
            "data": {"screen": "chat"}
        }
        requests.post("https://onesignal.com/api/v1/notifications", headers=headers, data=json.dumps(payload))
        
        print("OneSignal status:", response.status_code, response.text)
