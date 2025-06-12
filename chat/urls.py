from django.urls import path
from .views import chat_history

urlpatterns = [
    path('history/<int:user1_id>/<int:user2_id>/', chat_history),
]