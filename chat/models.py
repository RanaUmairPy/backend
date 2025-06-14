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