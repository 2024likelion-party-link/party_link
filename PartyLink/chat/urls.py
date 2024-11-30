from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_room, name='create_room'),
    path('room/<uuid:room_id>/', views.room, name='room'),
]
