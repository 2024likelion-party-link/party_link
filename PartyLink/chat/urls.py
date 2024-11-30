from django.urls import path
from .views import RoomDetailView, SendMessageView

urlpatterns = [
    path("rooms/<uuid:room_id>/", RoomDetailView.as_view(), name="room-detail"),
    path("rooms/<uuid:room_id>/send/", SendMessageView.as_view(), name="send-message"),
]
