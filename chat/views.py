from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializer import MessageSerializer
from .models import Player
from rest_framework import viewsets
from .models import OneSignal
from .serializer import OneSignalSerializer

@api_view(['GET'])
def chat_history(request, user1_id, user2_id):
    messages = Message.objects.filter(
        sender_id__in=[user1_id, user2_id],
        receiver_id__in=[user1_id, user2_id]
    ).order_by('timestamp')
    return Response(MessageSerializer(messages, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def store_player_id(request):
    user = request.user
    player_id = request.data.get('player_id')

    if not player_id:
        return Response({"error": "player_id is required"}, status=400)

    Player.objects.update_or_create(user=user, defaults={"player_id": player_id})
    return Response({"status": "Player ID saved"})


class OneSignalViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = OneSignalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Player ID stored"}, status=201)
        return Response(serializer.errors, status=400)
