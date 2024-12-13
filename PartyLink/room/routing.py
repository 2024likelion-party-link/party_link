from django.urls import path, re_path
from .consumers import RoomConsumer

websocket_urlpatterns = [
    re_path(r'ws/room/(?P<room_id>[^/]+)/$', RoomConsumer.as_asgi()),
]