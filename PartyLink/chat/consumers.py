import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # 방에 참가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # 방에서 나가기
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = data["sender"]
        content = data["content"]

        # 메시지를 데이터베이스에 저장
        room = await ChatRoom.objects.aget(room_id=self.room_id)
        await Message.objects.acreate(room=room, sender=sender, content=content)

        # 메시지를 방의 다른 사용자들에게 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender": sender,
                "content": content,
            },
        )

    async def chat_message(self, event):
        # 클라이언트로 메시지 전송
        await self.send(text_data=json.dumps({"sender": event["sender"], "content": event["content"]}))
