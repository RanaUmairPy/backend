# backend/asgi.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ✅ set environment first
django.setup()  # ✅ setup before importing anything using models

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns  # ✅ import AFTER setup()

application = ProtocolTypeRouter({
    "http": django.core.asgi.get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
