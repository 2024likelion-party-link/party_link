from django.urls import path
from .views import ChatRoomListCreateView, ChatMessageListView, ChatMessageCreateView

urlpatterns = [
    path("rooms/", ChatRoomListCreateView.as_view(), name="chat-room-list-create"),
    path("rooms/<int:room_id>/messages/", ChatMessageListView.as_view(), name="chat-message-list"),
    path("rooms/<int:room_id>/messages/create/", ChatMessageCreateView.as_view(), name="chat-message-create"),
]
