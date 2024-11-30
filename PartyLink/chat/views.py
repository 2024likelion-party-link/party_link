from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer


class MessageView(APIView):
    def get(self, request, room_id):
        # 특정 채팅방의 메시지 조회
        try:
            room = Message.objects.get(room_id=room)
            messages = room.messages.all()
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, room_id):
        # 특정 채팅방에 메시지 생성
        try:
            room = Message.objects.get(room_id=room)
            data = request.data
            data["room"] = room.id
            serializer = MessageSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Message.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
