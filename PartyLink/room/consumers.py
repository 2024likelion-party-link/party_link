import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Participant
from django.core.cache import cache

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        # 참가자가 방에 연결되면, WebSocket 연결을 허용
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # 기존 참가자 목록 보내기
        participants_key = f"room:{self.room_id}:participants"
        participants = cache.lrange(participants_key, 0, -1)
        participants_data = [p.decode('utf-8').split(":")[1] for p in participants]
        await self.send(json.dumps({'participants': participants_data}))

    async def disconnect(self, close_code):
        # 참가자가 나가면 목록에서 제거
        participants_key = f"room:{self.room_id}:participants"
        cache.lrem(participants_key, 0, self.channel_name)  # 채널을 이용해 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        nickname = data['nickname']

        # 참가자 추가
        participants_key = f"room:{self.room_id}:participants"
        participant_id = str(uuid.uuid4())  # 고유 ID 생성
        cache.lpush(participants_key, f"{participant_id}:{nickname}")

        # 실시간 참가자 목록 업데이트
        participants = cache.lrange(participants_key, 0, -1)
        participants_data = [p.decode('utf-8').split(":")[1] for p in participants]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_participants',
                'participants': participants_data
            }
        )

    
    async def send_participants(self, event):
        await self.send(json.dumps({'participants': event['participants']}))
