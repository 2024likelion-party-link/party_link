import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.conf import settings
import redis

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"room_{self.room_id}"

        # 그룹에 참가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # WebSocket 메시지 처리
        data = json.loads(text_data)

        # 쿠키에서 사용자 토큰 확인
        user_token = self.scope["cookies"].get("user_token")
        if not user_token:
            await self.send(json.dumps({"error": "Authentication required"}))
            return

        sender = redis_client.get(f"user:{user_token}:nickname")
        if not sender:
            await self.send(json.dumps({"error": "Invalid token"}))
            return

        sender = sender.decode()  # Redis 값 디코딩
        content = data["content"]

        # 그룹에 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "sender": sender,
                "content": content,
            },
        )

    async def chat_message(self, event):
        # 메시지를 WebSocket으로 전송
        await self.send(
            text_data=json.dumps(
                {
                    "sender": event["sender"],
                    "content": event["content"],
                    "timestamp": event.get("timestamp", ""),
                }
            )
        )
