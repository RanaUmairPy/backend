from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def file_url(self):
        if self.file:
            return self.file.url
        return None

    def as_dict(self):
        return {
            "id": self.id,
            "sender": self.sender.id,
            "receiver": self.receiver.id,
            "text": self.text,
            "file_url": self.file_url(),
            "filename": self.filename,
            "timestamp": self.timestamp.isoformat(),
        }
        
class Player(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.player_id}'

class OneSignal(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onesignal')
    player_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.player_id}"
