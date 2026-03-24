"""
Serializers for Lab API.
"""
from rest_framework import serializers
from .models import SimulatedEnvironment, Lab, LabAttempt, CommandLog


class SimulatedEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatedEnvironment
        fields = ['id', 'name', 'description', 'simulated_user', 'simulated_hostname']


class LabListSerializer(serializers.ModelSerializer):
    """Minimal lab info for listings."""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = Lab
        fields = ['id', 'title', 'description', 'difficulty', 'xp_reward', 
                  'time_limit', 'objective_count', 'lesson_title']


class LabDetailSerializer(serializers.ModelSerializer):
    """Full lab details for starting a lab."""
    environment = SimulatedEnvironmentSerializer(read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = Lab
        fields = ['id', 'title', 'description', 'instructions', 'difficulty',
                  'xp_reward', 'time_limit', 'environment', 'objectives',
                  'objective_count', 'lesson_title']
        # Note: hints and flags are NOT exposed (revealed progressively)


class LabAttemptSerializer(serializers.ModelSerializer):
    """Lab attempt status."""
    lab_title = serializers.CharField(source='lab.title', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = LabAttempt
        fields = ['id', 'lab', 'lab_title', 'completed', 'completed_objectives',
                  'hints_used', 'commands_executed', 'progress_percentage',
                  'started_at', 'completed_at']
        read_only_fields = ['completed_objectives', 'hints_used', 'commands_executed',
                           'started_at', 'completed_at']


class CommandExecuteSerializer(serializers.Serializer):
    """Serializer for executing a command."""
    command = serializers.CharField(max_length=500)


class CommandResponseSerializer(serializers.Serializer):
    """Serializer for command execution response."""
    output = serializers.CharField()
    return_code = serializers.IntegerField()
    is_error = serializers.BooleanField()
    prompt = serializers.CharField()
    objectives_completed = serializers.ListField(child=serializers.IntegerField())


class HintSerializer(serializers.Serializer):
    """Serializer for hint response."""
    hint_number = serializers.IntegerField()
    hint_text = serializers.CharField()
    hints_remaining = serializers.IntegerField()


class FlagSubmitSerializer(serializers.Serializer):
    """Serializer for CTF flag submission."""
    flag = serializers.CharField(max_length=200)


class FlagResponseSerializer(serializers.Serializer):
    """Serializer for flag submission response."""
    correct = serializers.BooleanField()
    message = serializers.CharField()
    xp_earned = serializers.IntegerField()
