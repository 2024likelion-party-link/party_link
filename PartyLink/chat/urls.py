from django.urls import path
from .views import ChatRoomListCreateView, MessageListCreateView

urlpatterns = [
    path('rooms/', ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('rooms/<int:room_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
]
