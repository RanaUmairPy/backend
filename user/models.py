from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.conf import settings
class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, blank=True, null=True)

    def generate_otp(self):
        self.email_otp = str(random.randint(100000, 999999))
        self.save()
    
    def verify_otp(self, otp):
        if self.email_otp == otp:
            self.is_email_verified = True
            self.email_otp = None
            self.save()
            return True
        return False

    def __str__(self):
        return self.username


class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({'Accepted' if self.is_accepted else 'Pending'})"


class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"
