from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser, FriendRequest, Friendship
from .serializer import CustomUserSerializer, FriendRequestSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .utils import send_otp_email


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    #permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        user = serializer.save(password=make_password(serializer.validated_data['password']))
        user.generate_otp()
        # You can add sending OTP email here
        send_otp_email(user)
        return Response({'message': 'User created, OTP sent!', 'user': serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        try:
            user = CustomUser.objects.get(email=email)
            if user.verify_otp(otp):
                return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        identifier = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({'error': 'Username/email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if '@' in str(identifier):
            user = CustomUser.objects.filter(email=identifier).first()
        else:
            user = CustomUser.objects.filter(username=identifier).first()

        if user and check_password(password, user.password):
            if not user.is_email_verified:
                return Response({'error': 'Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = CustomUserSerializer(user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid username/email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['get'], url_path='search')
    def search_users(self, request):
        query = request.query_params.get('q', '')
        current_user = request.user

        if not query:
            return Response([], status=status.HTTP_200_OK)

        users = CustomUser.objects.filter(username__icontains=query).exclude(id=current_user.id)
        results = []
        for user in users:
            # Check friendship
            is_friend = Friendship.objects.filter(
                user1=current_user, user2=user
            ).exists()

            # Check if friend request pending (sent or received)
            request_sent = FriendRequest.objects.filter(from_user=current_user, to_user=user, is_accepted=False).exists()
            request_received = FriendRequest.objects.filter(from_user=user, to_user=current_user, is_accepted=False).exists()

            status = "none"
            if is_friend:
                status = "friends"
            elif request_sent:
                status = "pending_sent"
            elif request_received:
                status = "pending_received"

            serializer = CustomUserSerializer(user)
            data = serializer.data
            data['friendship_status'] = status
            results.append(data)

        return Response(results)
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='friends')
    def user_friends(self, request):
        user = request.user
        # Get all friendships where the current user is user1
        friendships = Friendship.objects.filter(user1=user)
        friends = [f.user2 for f in friendships]
        serializer = CustomUserSerializer(friends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh_token(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response(
                {'access': access_token},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optionally filter friend requests relevant to the logged-in user
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user) | FriendRequest.objects.filter(from_user=user)

    def create(self, request, *args, **kwargs):
        from_user = request.user
        to_user_id = request.data.get("to_user")

        if not to_user_id:
            return Response({'error': 'To user is required'}, status=status.HTTP_400_BAD_REQUEST)

        if str(from_user.id) == str(to_user_id):
            return Response({'error': 'Cannot send request to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_user = CustomUser.objects.get(id=to_user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'To user not found'}, status=status.HTTP_404_NOT_FOUND)

        exists = FriendRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).exists() or FriendRequest.objects.filter(
            from_user=to_user, to_user=from_user
        ).exists()

        if exists:
            return Response({'error': 'Friend request already exists'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()

        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        try:
            friend_request = self.get_object()
            if friend_request.is_accepted:
                return Response({'message': 'Request already accepted'}, status=status.HTTP_200_OK)

            friend_request.is_accepted = True
            friend_request.save()

            # Create reciprocal friendships
            Friendship.objects.get_or_create(user1=friend_request.from_user, user2=friend_request.to_user)
            Friendship.objects.get_or_create(user1=friend_request.to_user, user2=friend_request.from_user)

            return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        try:
            friend_request = self.get_object()
            friend_request.delete()
            return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='received')
    def received_requests(self, request):
        user = request.user
        requests = FriendRequest.objects.filter(to_user=user, is_accepted=False)
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)
    




