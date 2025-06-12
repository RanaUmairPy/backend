from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Message
from .serializer import MessageSerializer

@api_view(['GET'])
def chat_history(request, user1_id, user2_id):
    messages = Message.objects.filter(
        sender_id__in=[user1_id, user2_id],
        receiver_id__in=[user1_id, user2_id]
    ).order_by('timestamp')
    return Response(MessageSerializer(messages, many=True).data)