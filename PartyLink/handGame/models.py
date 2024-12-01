# handgame/models.py
from django.db import models
import random
from room.models import Participant, Room

class Game(models.Model):
    game = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='game')
    is_active = models.BooleanField(default=True)  # Track if the game is active
    current_round = models.IntegerField(default=1)  # Track the current round number
    loser = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True, blank=True)  # Track the loser of the game

    def start_next_round(self):
        self.current_round += 1
        self.save()

    def end_game(self, loser: Participant):
        self.is_active = False
        self.loser = loser
        self.save()

    def __str__(self):
        return f"Game in Room {self.room.room_id}"

class PlayerState(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    fingers = models.IntegerField(default=5)  # Start with 5 fingers
    is_active = models.BooleanField(default=True)  # Track if the participant is still in the game

    def reduce_finger(self):
        if self.fingers > 0:
            self.fingers -= 1
            self.save()
    
    def undo_finger_reduction(self):
        if self.fingers < 5 :
            self.fingers += 1
            self.save()

    def __str__(self):
        return f"{self.participant.nickname} ({self.fingers} fingers)"
