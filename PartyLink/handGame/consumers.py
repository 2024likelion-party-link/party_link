import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game, PlayerState
from room.models import Participant, Room

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"game_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        participant_id = data.get('participant_id')

        if action == 'reduce_finger':
            await self.reduce_finger(participant_id)
        elif action == 'game_status':
            await self.send_game_status()

    async def reduce_finger(self, participant_id):
        try:
            player = PlayerState.objects.get(participant__id=participant_id)
            game = Game.objects.get(game__participant__id=participant_id, is_active=True)

            # Reduce finger count
            player.reduce_finger()

            # Check for game over
            if player.fingers == 0:
                game.end_game(player.participant)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over',
                        'loser': player.participant.nickname,
                        'message': f"{player.participant.nickname} lost the game!"
                    }
                )
            else:
                # Notify group of updated status
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_finger_count',
                        'nickname': player.participant.nickname,
                        'fingers': player.fingers
                    }
                )
        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def send_game_status(self):
        game = Game.objects.filter(game__room_id=self.room_id).first()
        players = PlayerState.objects.filter(participant__room_id=self.room_id)

        await self.send(text_data=json.dumps({
            "is_active": game.is_active,
            "current_round": game.current_round,
            "players": [
                {"nickname": player.participant.nickname, "fingers": player.fingers}
                for player in players
            ],
            "loser": game.loser.nickname if game.loser else None
        }))

    # Handlers for group messages
    async def update_finger_count(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_finger_count',
            'nickname': event['nickname'],
            'fingers': event['fingers']
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'loser': event['loser'],
            'message': event['message']
        }))
