from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import chat_history,store_player_id,OneSignalViewSet

router = DefaultRouter()
router.register(r'store_player_id', OneSignalViewSet, basename='store-player-id')
urlpatterns = [
    path('history/<int:user1_id>/<int:user2_id>/', chat_history),
    path('api/', include(router.urls)),
]
