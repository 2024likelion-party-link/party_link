from django.urls import path
from .views import CreateRoomView,GetGamesView

urlpatterns = [
    path('create-room/', CreateRoomView.as_view(), name='create-room'),
    path('games/', GetGamesView.as_view(), name='get_games'),
]