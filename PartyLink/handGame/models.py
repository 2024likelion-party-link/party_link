from django.db import models
import uuid
from room.models import Room

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]