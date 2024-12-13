import time
import uuid
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room  # Assuming Room model exists
import redis

# Initialize redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class CreateRoomView(APIView):
    def post(self, request):
        host_name = request.data.get('host_name')

        if not host_name:
            return Response({"error": "host_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Room 객체 생성
        room = Room.objects.create(host_name=host_name)

        room_info_key = f"room:{room.room_id}:info"
        
        # If the key exists and is not a hash, delete it to avoid type conflicts
        if redis_client.exists(room_info_key):
            current_type = redis_client.type(room_info_key)
            if current_type != b'hash':  # Not a hash, so delete it
                redis_client.delete(room_info_key)

        # Set the room information as a hash and store the host_name
        redis_client.hset(room_info_key, "host_name", host_name)
        redis_client.expire(room_info_key, 3600)  # TTL for the room info (1 hour)

        # Store the participants (using a sorted set)
        timestamp = time.time()

        # 유저 아이디 생성
        user_id = str(uuid.uuid4())
        
        # # 사용자 이름과 user_id를 Redis에 저장
        # redis_client.hset(f"user:{user_id}", "nickname", host_name)

        # 참가자 목록에 해당 user_id와 nickname을 추가
        redis_client.zadd(f"room:{room.room_id}:participants", {f"{host_name}:host": timestamp})

        # 응답으로 user_id와 room_id 반환
        return Response({
            "room_id": str(room.room_id),
            "nickname": host_name
        }, status=status.HTTP_201_CREATED)


# 게임 목록 반환
class GetGamesView(APIView):
    def get(self, request):
        games = [
            {"id": "handGame", "name": "손병호 게임"},
            {"id": "imageGame", "name": "이미지 게임"},
        ]
        return Response({"games": games}, status=status.HTTP_200_OK)
