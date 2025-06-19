from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'onesignal', views.OneSignalViewSet, basename='onesignal')

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('download/<int:message_id>/', views.serve_file, name='serve_file'),
    path('chat/<int:user1_id>/<int:user2_id>/', views.chat_history, name='chat_history'),
    path('store-player-id/', views.store_player_id, name='store_player_id'),
] + router.urls
