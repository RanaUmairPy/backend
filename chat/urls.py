from django.urls import path
from .views import chat_history,store_player_id

urlpatterns = [
    path('history/<int:user1_id>/<int:user2_id>/', chat_history),
    path('api/store_player_id/', store_player_id, name='store_player_id'),
]
