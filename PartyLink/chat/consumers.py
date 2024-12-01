import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        WebSocket 연결을 처리. 클라이언트를 특정 채팅방 그룹에 추가.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # URL 경로에서 채팅방 이름 추출
        self.room_group_name = f'chat_{self.room_name}'  # 그룹 이름 지정

        # 그룹에 추가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        WebSocket 연결이 종료되었을 때 클라이언트를 그룹에서 제거.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        클라이언트로부터 메시지를 수신했을 때 처리.
        """
        data = json.loads(text_data)
        username = data['username']
        content = data['content']

        # 메시지를 데이터베이스에 저장
        message = await self.save_message(self.room_name, username, content)

        # 메시지를 그룹에 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # 처리할 메서드 이름
                'username': username,
                'content': content,
                'timestamp': message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        """
        그룹 메시지를 클라이언트로 전송.
        """
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'content': event['content'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, room_name, username, content):
        """
        데이터베이스에 메시지를 저장하는 동기 작업을 비동기로 감싸 처리.
        """
        room, _ = ChatRoom.objects.get_or_create(name=room_name)
        return Message.objects.create(chatroom=room, username=username, content=content)
