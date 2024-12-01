from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Game, PlayerState
from room.models import Room, Participant
import random

class StartGameAPIView(APIView):
    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        participants = room.participant_set.all()

        if len(participants) != 5:
            return Response({"error": "The game requires exactly 5 participants."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the game
        game = Game.objects.create(game=room)
        random_order = list(participants)
        random.shuffle(random_order)

        # Initialize player states
        for participant in random_order:
            PlayerState.objects.create(participant=participant)

        return Response({
            "message": "Game started successfully",
            "order": [participant.nickname for participant in random_order]
        }, status=status.HTTP_201_CREATED)


class SubmitActionAPIView(APIView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id, is_active=True)
        participant_id = request.data.get("participant_id")
        participant = get_object_or_404(PlayerState, participant__id=participant_id)

        # Reduce fingers for this participant
        participant.reduce_finger()

        # Check if the participant has lost
        if participant.fingers == 0:
            game.end_game(participant.participant)
            return Response({
                "message": f"{participant.participant.nickname} lost the game!",
                "loser": participant.participant.nickname
            }, status=status.HTTP_200_OK)

        # Proceed to the next round
        game.start_next_round()
        return Response({
            "message": "Action submitted successfully",
            "current_round": game.current_round
        }, status=status.HTTP_200_OK)


class GameStatusAPIView(APIView):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        players = PlayerState.objects.filter(participant__room=game.game)

        return Response({
            "is_active": game.is_active,
            "current_round": game.current_round,
            "players": [
                {"nickname": player.participant.nickname, "fingers": player.fingers}
                for player in players
            ],
            "loser": game.loser.nickname if game.loser else None
        })
