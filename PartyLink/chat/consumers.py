import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .serializers import ChatMessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # JWT 토큰 검증
        user = await self.authenticate_user()
        if not user:
            await self.close()
            return

        self.user = user
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        serializer = ChatMessageSerializer(data=text_data_json)

        if serializer.is_valid():
            message = serializer.validated_data["message"]

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "user": self.user.username,
                },
            )
        else:
            await self.send(
                text_data=json.dumps({"error": "Invalid message format"})
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        user = event["user"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({"user": user, "message": message})
        )

    async def authenticate_user(self):
        """Authenticate user using DRF's JWT."""
        try:
            jwt_auth = JWTAuthentication()
            scope_headers = self.scope.get("headers")
            headers_dict = {k.decode("utf-8"): v.decode("utf-8") for k, v in scope_headers}
            token = headers_dict.get("authorization", "").split("Bearer ")[-1]

            if not token:
                return None

            user, _ = jwt_auth.authenticate_credentials(token)
            return user
        except (AuthenticationFailed, KeyError):
            return None
