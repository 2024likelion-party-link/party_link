from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRoom, Message

class RoomDetailView(APIView):
    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(room_id=room_id)
            messages = Message.objects.filter(room=room).values("sender", "content", "timestamp")
            return Response({"room_id": room_id, "messages": list(messages)}, status=status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room does not exist"}, status=status.HTTP_404_NOT_FOUND)

class SendMessageView(APIView):
    def post(self, request, room_id):
        sender = request.data.get("sender")
        content = request.data.get("content")

        if not sender or not content:
            return Response({"error": "sender and content are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = ChatRoom.objects.get(room_id=room_id)
            message = Message.objects.create(room=room, sender=sender, content=content)
            return Response({"sender": message.sender, "content": message.content, "timestamp": message.timestamp}, status=status.HTTP_201_CREATED)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room does not exist"}, status=status.HTTP_404_NOT_FOUND)
