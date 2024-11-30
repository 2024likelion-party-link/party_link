from django.shortcuts import render, redirect
from .models import ChatRoom

def create_room(request):
    if request.method == "POST":
        name = request.POST.get("name")
        room = ChatRoom.objects.create(name=name)
        return redirect(f'/chat/room/{room.room_id}/?nickname={name}')
    return render(request, 'create_room.html')

def room(request, room_id):
    nickname = request.GET.get('nickname', 'Anonymous')
    return render(request, 'room.html', {"room_id": room_id, "nickname":nickname})
