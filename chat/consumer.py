import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

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
                'file': msg_obj.file_url(),
                'filename': msg_obj.filename,
                'sender_id': msg_obj.sender.id,
                'receiver_id': msg_obj.receiver.id,
                'timestamp': msg_obj.timestamp.isoformat(),
            }
        )

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