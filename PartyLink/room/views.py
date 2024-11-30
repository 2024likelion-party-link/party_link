from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room
import redis
import time

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)

class CreateRoomView(APIView):
    def post(self, request):
        host_name = request.data.get('host_name')

        if not host_name:
            return Response(
                {"error": "host_name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Room 객체 생성
        room = Room.objects.create(host_name=host_name)

        redis_client.set(f"room:{room.room_id}:info", "created")
        # 호스트를 Redis에 저장 (nickname:role 형식으로 저장)
        timestamp = time.time()  # 현재 시간으로 참여 순서 추적
        redis_client.zadd(f"room:{room.room_id}:participants", {f"{host_name}:host": timestamp})

        return Response({"room_id": str(room.room_id)}, status=status.HTTP_201_CREATED)

# class JoinRoomView(APIView):
#     def post(self, request, room_id):
#         nickname = request.data.get('nickname')

#         # 참가자 역할 설정 (기본값: 'participant')
#         role = 'participant'

#         # 참가자를 방에 추가할 때 역할과 함께 저장
#         timestamp = time.time()  # 현재 시간으로 참여 순서 추적

#         # 참가자가 방에 추가되면 성공 (참여자가 이미 존재하면 False 반환)
#         added = redis_client.zadd(f"room:{room_id}:participants", {f"{nickname}:{role}": timestamp})
        
#         if added:
#             return Response({"message": "Joined room"}, status=status.HTTP_200_OK)
#         return Response({"error": "Failed to join room"}, status=status.HTTP_400_BAD_REQUEST)


class JoinRoomView(APIView):
    def post(self, request, room_id):
        nickname = request.data.get('nickname')

        if not nickname:
            return Response(
                {"error": "nickname is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 참가자 역할 설정 (기본값: 'participant')
        role = 'participant'

        # Redis에 닉네임과 역할 저장
        timestamp = time.time()
        added = redis_client.zadd(f"room:{room_id}:participants", {f"{nickname}:{role}": timestamp})
        
        if added:
            return Response({"message": "Joined room", "room_id": room_id, "nickname": nickname}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to join room"}, status=status.HTTP_400_BAD_REQUEST)

class GetParticipantsView(APIView):
    def get(self, request, room_id):
        # Redis에서 방에 참가한 참가자 목록을 참여 순서대로 가져오기
        participants = redis_client.zrange(f"room:{room_id}:participants", 0, -1)

        # Redis는 바이트 형식으로 저장되므로 이를 디코딩하고 'nickname:role'로 분리
        participants_list = []
        for participant in participants:
            nickname, role = participant.decode().split(":")
            participants_list.append({"nickname": nickname, "role": role})

        
        return Response({"participants": participants_list})

# 게임 목록 반환
class GetGamesView(APIView):
    def get(self, request):
        games = [
            {"id": "handGame", "name": "손병호 게임"},
            {"id": "imageGame", "name": "이미지 게임"}
        ]
        return Response({"games": games}, status=status.HTTP_200_OK)