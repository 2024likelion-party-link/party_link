import uuid
import redis
import time
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)


class CreateRoomView(APIView):
    def post(self, request):
        host_name = request.data.get('host_name')

        if not host_name:
            return Response({"error": "host_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Room 객체 생성
        room = Room.objects.create(host_name=host_name)

        # Redis에 방 정보 저장
        redis_client.set(f"room:{room.room_id}:info", "created", ex=3600)  # TTL 1시간
        timestamp = time.time()
        redis_client.zadd(f"room:{room.room_id}:participants", {f"{host_name}:host": timestamp})
        redis_client.expire(f"room:{room.room_id}:participants", 3600)  # TTL 1시간

        # 사용자 토큰 생성 및 저장
        user_token = get_random_string(32)
        redis_client.set(f"user:{user_token}:nickname", host_name, ex=3600)

        # 쿠키에 토큰 설정
        response = Response({"room_id": str(room.room_id)}, status=status.HTTP_201_CREATED)
        response.set_cookie("user_token", user_token, httponly=True, max_age=3600)

        return response


class JoinRoomView(APIView):
    def post(self, request, room_id):
        nickname = request.data.get('nickname')

        if not nickname:
            return Response({"error": "Nickname is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Redis 중복 확인
        existing_participants = redis_client.zrange(f"room:{room_id}:participants", 0, -1)
        for participant in existing_participants:
            existing_nickname, _ = participant.decode().split(":")
            if existing_nickname == nickname:
                return Response({"error": "Nickname already in use"}, status=status.HTTP_400_BAD_REQUEST)

        # Redis에 참가자 추가
        timestamp = time.time()
        role = 'participant'
        redis_client.zadd(f"room:{room_id}:participants", {f"{nickname}:{role}": timestamp})
        redis_client.expire(f"room:{room_id}:participants", 3600)  # TTL 1시간

        # 사용자 토큰 생성 및 저장
        user_token = get_random_string(32)
        redis_client.set(f"user:{user_token}:nickname", nickname, ex=3600)

        # 쿠키에 토큰 설정
        response = Response({"message": "Joined room"}, status=status.HTTP_200_OK)
        response.set_cookie("user_token", user_token, httponly=True, max_age=3600)
        return response


class GetParticipantsView(APIView):
    def get(self, request, room_id):
        # 쿠키에서 사용자 토큰 확인
        user_token = request.COOKIES.get("user_token")
        current_user = redis_client.get(f"user:{user_token}:nickname").decode() if user_token else None

        # Redis에서 방에 참가한 참가자 목록을 가져옴
        participants = redis_client.zrange(f"room:{room_id}:participants", 0, -1)

        # 참가자 정보 파싱
        participants_list = []
        for participant in participants:
            nickname, role = participant.decode().split(":")
            display_nickname = f"{nickname} (나)" if nickname == current_user else nickname
            participants_list.append({"nickname": display_nickname, "role": role})

        return Response({"participants": participants_list}, status=status.HTTP_200_OK)


# 게임 목록 반환
class GetGamesView(APIView):
    def get(self, request):
        games = [
            {"id": "handGame", "name": "손병호 게임"},
            {"id": "imageGame", "name": "이미지 게임"}
        ]
        return Response({"games": games}, status=status.HTTP_200_OK)
