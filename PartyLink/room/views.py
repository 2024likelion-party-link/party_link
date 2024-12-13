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

# ========== Views ===========
def create_room(request):
    if request.method == 'POST':
        room_id = str(uuid.uuid4())
        room_link = f'/room/{room_id}/'
        return JsonResponse({'room_id': room_id, 'room_link': room_link})
    return JsonResponse({'error': 'Invalid method'}, status=400)

def room_view(request, room_id):
    return render(request, 'room.html', {'room_id': room_id})
