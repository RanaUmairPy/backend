from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.http import HttpResponse, Http404
from .models import Message, OneSignal
from .serializers import MessageSerializer, OneSignalSerializer

ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    if not request.FILES.get('file'):
        return Response({"error": "File is required"}, status=400)
    file = request.FILES['file']
    if file.content_type not in ALLOWED_TYPES:
        return Response({"error": "Invalid file type"}, status=400)
    if file.size > MAX_SIZE:
        return Response({"error": "File too large"}, status=400)
    msg = Message.objects.create(
        sender=request.user,
        filename=file.name,
        file=file
    )
    return Response({"file_url": msg.file_url(), "filename": file.name}, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_file(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        if message.sender != request.user and message.receiver != request.user:
            raise Http404("Unauthorized")
        with open(message.file.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{message.filename}"'
            return response
    except Message.DoesNotExist:
        raise Http404("File not found")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request, user1_id, user2_id):
    messages = Message.objects.filter(
        sender_id__in=[user1_id, user2_id],
        receiver_id__in=[user1_id, user2_id]
    ).order_by('timestamp')
    return Response(MessageSerializer(messages, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def store_player_id(request):
    serializer = OneSignalSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Player ID stored"}, status=201)
    return Response(serializer.errors, status=400)

class OneSignalViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = OneSignalSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Player ID stored"}, status=201)
        return Response(serializer.errors, status=400)
