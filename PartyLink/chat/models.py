from django.db import models
import uuid

class Room(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)  # 닉네임

class ChatRoom(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # 고유한 UUID 방 ID
    name = models.CharField(max_length=255)  # 방 이름
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 날짜

    def __str__(self):
        return self.name
    
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=255)  # 보낸 사람
    text = models.TextField()  # 메시지 내용
    timestamp = models.DateTimeField(auto_now_add=True)  # 보낸 시간

    def __str__(self):
        return f'{self.sender}: {self.text[:50]}'

class ShopUser(models.Model):
    username = models.CharField(max_length=255, unique=True)  # 사용자 이름

    def __str__(self):
        return self.username

class VisitorUser(models.Model):
    username = models.CharField(max_length=255, unique=True)  # 방문자 이름
    joined_at = models.DateTimeField(auto_now_add=True)  # 입장 시간

    def __str__(self):
        return self.username
