import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Participant

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        # 방 그룹에 WebSocket 추가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 방 그룹에서 WebSocket 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'join':
            nickname = data['nickname']
            await self.add_participant(nickname)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'room_message',
                    'message': f'{nickname} joined the room!'
                }
            )
        elif action == 'leave':
            nickname = data['nickname']
            await self.remove_participant(nickname)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'room_message',
                    'message': f'{nickname} left the room.'
                }
            )

    async def room_message(self, event):
        message = event['message']

        # WebSocket에 메시지 보내기
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @sync_to_async
    def add_participant(self, nickname):
        room = Room.objects.get(room_id=self.room_id)
        Participant.objects.get_or_create(room=room, nickname=nickname, role='participant')

    @sync_to_async
    def remove_participant(self, nickname):
        room = Room.objects.get(room_id=self.room_id)
        Participant.objects.filter(room=room, nickname=nickname).delete()
