import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.conf import settings
import redis

# Redis 클라이언트 설정
use_redis = hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT')
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0) if use_redis else None


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'
        
        # 메모리 기반 접근 초기화
        if not hasattr(self.channel_layer, "rooms"):
            self.channel_layer.rooms = {}
        if self.room_id not in self.channel_layer.rooms:
            self.channel_layer.rooms[self.room_id] = {}

        # 그룹 추가 및 WebSocket 연결 허용
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # 기존 참가자 목록 전송
        participants = await self.get_participants()
        await self.send(json.dumps({'type': 'participants', 'participants': participants}))

    async def disconnect(self, close_code):
        if use_redis:
            participants_key = f"room:{self.room_id}:participants"
            redis_client.lrem(participants_key, 0, self.channel_name)
        else:
            if self.room_id in self.channel_layer.rooms:
                self.channel_layer.rooms[self.room_id].pop(self.channel_name, None)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'join':
            nickname = data['nickname']
            user_id = str(uuid.uuid4())

            # 참가자 추가
            await self.add_participant(nickname, user_id)

            # 참가자 목록 갱신 및 그룹 전송
            participants = await self.get_participants()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    'message': {
                        'type': 'join',
                        'nickname': nickname,
                        'userId': user_id,
                        'participants': participants
                    }
                }
            )

            # 본인에게 고유 ID 전송
            await self.send(json.dumps({'type': 'self_id', 'userId': user_id}))

        elif message_type == 'message':
            # 메시지 처리 로직 추가 가능
            pass

    async def send_message(self, event):
        await self.send(json.dumps(event['message']))

    async def add_participant(self, nickname, user_id):
        if use_redis:
            participants_key = f"room:{self.room_id}:participants"
            redis_client.lpush(participants_key, f"{user_id}:{nickname}")
        else:
            self.channel_layer.rooms[self.room_id][self.channel_name] = {'nickname': nickname, 'user_id': user_id}

    async def get_participants(self):
        if use_redis:
            participants_key = f"room:{self.room_id}:participants"
            participants = redis_client.lrange(participants_key, 0, -1)
            return [{'userId': p.decode('utf-8').split(':')[0], 'nickname': p.decode('utf-8').split(':')[1]} for p in participants]
        else:
            if self.room_id in self.channel_layer.rooms:
                return [
                    {'userId': data['user_id'], 'nickname': data['nickname']}
                    for data in self.channel_layer.rooms[self.room_id].values()
                ]
            return []
