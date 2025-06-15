# backend/asgi.py

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns  # ✅ correct import
from django.core.asgi import get_asgi_application  # ✅ this is the correct import!

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # ✅ fixed here
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
