import jwt
import time
import uuid
from django.conf import settings

class TokenService:
    def __init__(self):
        self.app_access_key = settings.HMS_APP_ACCESS_KEY
        self.app_secret = settings.HMS_APP_SECRET

    def generate_token(self, user_id, room_id, role="speaker"):
        payload = {
            "access_key": self.app_access_key,
            "room_id": room_id,
            "user_id": str(user_id),
            "role": role,
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400,  # Token valid for 24 hours
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, self.app_secret, algorithm="HS256")
