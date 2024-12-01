from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/<uuid:room_id>/', consumers.GameConsumer.as_asgi()),
]
