from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from redis import Redis
from .models import Room, Participant

vredis_client = Redis(host='localhost', port=6379, decode_responses=True)

class CreateRoomView(APIView):
    def post(self, request):
        host_name = request.data.get('host_name')

        if not host_name:
            return Response({"error": "Host name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create room and host participant
        room = Room.objects.create(host_name=host_name)
        Participant.objects.create(room=room, nickname=host_name, role='host')
        return Response({"room_id": str(room.room_id)}, status=status.HTTP_201_CREATED)
    
class JoinRoomView(APIView):
    def post(self, request, room_id):
        nickname = request.data.get('nickname')
        room = get_object_or_404(Room, room_id=room_id)

        if not nickname:
            return Response({"error": "Nickname is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if nickname is unique within the room
        if Participant.objects.filter(room=room, nickname=nickname).exists():
            return Response({"error": "Nickname already taken in this room."}, status=status.HTTP_400_BAD_REQUEST)

        # Add participant to the room
        Participant.objects.create(room=room, nickname=nickname, role='participant')
        vredis_client.sadd(f"room:{room_id}", nickname)
        return Response({"message": f"{nickname} joined room {room_id}"}, status=status.HTTP_200_OK)

class ListParticipantsView(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(Room, room_id=room_id)

        # Get the nickname of the current user
        current_nickname = request.query_params.get('nickname')

        if not current_nickname:
            return Response({"error": "Nickname is required to identify yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve all participants in the room, including the host, sorted by the order they joined
        participants = Participant.objects.filter(room=room).order_by('id')

        # Build the list of participants' nicknames, adding "(나)" for the current participant
        participant_list = []
        for participant in participants:
            nickname = participant.nickname
            if nickname == current_nickname:
                nickname += " (나)"  # Append "(나)" for the current participant
            participant_list.append(nickname)

        return Response({"participants": participant_list}, status=status.HTTP_200_OK)