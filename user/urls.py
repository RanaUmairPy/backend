from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, FriendRequestViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'user', CustomUserViewSet, basename='user')
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-requests')

urlpatterns = [
    path('', include(router.urls)),  # /register/ for registration, /register/login/ for login
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]