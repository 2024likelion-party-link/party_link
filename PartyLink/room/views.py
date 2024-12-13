import time
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
        redis_client.zadd(f"room:{room.room_id}:participants", {f"{host_name}:host": timestamp})
        redis_client.expire(f"room:{room.room_id}:participants", 3600)  # TTL 1시간

        # 사용자 토큰 생성 및 저장
        user_token = get_random_string(32)
        redis_client.set(f"user:{user_token}:nickname", host_name, ex=3600)

        # 쿠키에 토큰 설정
        response = Response({"room_id": str(room.room_id)}, status=status.HTTP_201_CREATED)
        response.set_cookie("user_token", user_token, httponly=True, max_age=3600)

        return response


# 게임 목록 반환
class GetGamesView(APIView):
    def get(self, request):
        games = [
            {"id": "handGame", "name": "손병호 게임"},
            {"id": "imageGame", "name": "이미지 게임"},
        ]
        return Response({"games": games}, status=status.HTTP_200_OK)
