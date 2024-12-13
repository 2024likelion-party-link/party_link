import json
import uuid
from django.urls import path, re_path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer

from .views import create_room, room_view


urlpatterns = [
    path('create-room/', create_room, name='create-room'),
    path('room/<str:room_id>/', room_view, name='room-view'),
]