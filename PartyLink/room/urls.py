from django.urls import path
from .views import CreateRoomView, JoinRoomView, ListParticipantsView

urlpatterns = [
    path('create/', CreateRoomView.as_view(), name='create-room'),
    path('join/<uuid:room_id>/', JoinRoomView.as_view(), name='join-room'),
    path('participants/<uuid:room_id>/', ListParticipantsView.as_view(), name='list-participants'),
]
