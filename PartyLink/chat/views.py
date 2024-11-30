from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer


class ChatRoomListCreateView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

    def perform_create(self, serializer):
        serializer.save()


class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return ChatMessage.objects.filter(room_id=room_id).order_by("timestamp")


class ChatMessageCreateView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer

    def perform_create(self, serializer):
        # 메시지 저장
        message = serializer.save(user=self.request.user)

        # WebSocket을 통해 메시지 전송
        room_group_name = f"chat_{message.room.id}"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "chat.message",
                "message": message.message,
            },
        )
