from rest_framework import serializers
from .models import Game, PlayerState

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class PlayerStateSerializer(serializers.ModelSerializer):
    participant = serializers.CharField(source="participant.nickname")

    class Meta:
        model = PlayerState
        fields = ['participant', 'fingers', 'is_active']
