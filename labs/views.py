"""
API views for labs.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Lab, LabAttempt, CommandLog
from .serializers import (
    LabListSerializer, LabDetailSerializer, LabAttemptSerializer,
    CommandExecuteSerializer, CommandResponseSerializer,
    HintSerializer, FlagSubmitSerializer, FlagResponseSerializer
)
from .terminal import CommandParser, InputSanitizer
from .simulator import EnvironmentSimulator
from users.permissions import HasAcceptedEthicalAgreement


# Store simulators in memory (in production, use Redis or session)
_simulators = {}


def get_simulator(attempt: LabAttempt) -> EnvironmentSimulator:
    """Get or create a simulator for a lab attempt."""
    key = f"{attempt.user.id}_{attempt.lab.id}"
    
    if key not in _simulators:
        env_config = {}
        if attempt.lab.environment:
            env_config = {
                'filesystem': attempt.lab.environment.filesystem,
                'network_config': attempt.lab.environment.network_config,
                'simulated_user': attempt.lab.environment.simulated_user,
                'simulated_hostname': attempt.lab.environment.simulated_hostname,
            }
        _simulators[key] = EnvironmentSimulator(env_config)
    
    return _simulators[key]


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def lab_list(request):
    """List all active labs."""
    labs = Lab.objects.filter(is_active=True).select_related('lesson')
    serializer = LabListSerializer(labs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def lab_detail(request, lab_id):
    """Get lab details."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    serializer = LabDetailSerializer(lab)
    
    # Check if user has an existing attempt
    attempt = LabAttempt.objects.filter(user=request.user, lab=lab).first()
    
    response_data = serializer.data
    if attempt:
        response_data['attempt'] = LabAttemptSerializer(attempt).data
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def start_lab(request, lab_id):
    """Start or resume a lab attempt."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    
    # Get or create attempt
    attempt, created = LabAttempt.objects.get_or_create(
        user=request.user,
        lab=lab
    )
    
    # Initialize simulator
    simulator = get_simulator(attempt)
    
    return Response({
        'attempt': LabAttemptSerializer(attempt).data,
        'prompt': simulator.get_prompt(),
        'message': 'Lab started!' if created else 'Lab resumed.',
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def execute_command(request, lab_id):
    """Execute a command in the lab terminal."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    attempt = get_object_or_404(LabAttempt, user=request.user, lab=lab)
    
    # Check if already completed
    if attempt.completed:
        return Response({
            'error': 'Lab already completed.',
            'prompt': '',
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = CommandExecuteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Sanitize input
    raw_command = serializer.validated_data['command']
    sanitized = InputSanitizer.sanitize(raw_command)
    
    # Get allowed commands for this lab
    allowed_commands = lab.allowed_commands if lab.allowed_commands else None
    
    # Parse and execute
    parser = CommandParser(allowed_commands)
    parsed = parser.parse(sanitized)
    
    # Get simulator
    simulator = get_simulator(attempt)
    result = simulator.execute(parsed)
    
    # Log the command
    CommandLog.objects.create(
        attempt=attempt,
        command=sanitized,
        output=result.output[:5000],  # Limit stored output
        was_blocked=not parsed.is_valid,
        blocked_reason=parsed.error_message if not parsed.is_valid else ''
    )
    
    # Update attempt stats
    attempt.commands_executed += 1
    attempt.save(update_fields=['commands_executed'])
    
    # Check for objective completion
    completed_objectives = check_objectives(attempt, parsed, result)
    
    return Response({
        'output': result.output,
        'return_code': result.return_code,
        'is_error': result.is_error,
        'prompt': simulator.get_prompt(),
        'objectives_completed': completed_objectives,
    })


def check_objectives(attempt: LabAttempt, parsed, result) -> list:
    """Check if any objectives were completed by the command."""
    if not attempt.lab.objectives:
        return []
    
    newly_completed = []
    objectives = attempt.lab.objectives
    flags = attempt.lab.flags or []
    
    for i, obj in enumerate(objectives):
        if i in attempt.completed_objectives:
            continue
        
        # Check if this objective requires previous objectives to be completed
        # By default, objectives are sequential unless marked as independent
        if isinstance(obj, dict) and obj.get('independent', False):
            # This objective can be completed independently
            pass
        elif i > 0:
            # Check if all previous objectives are completed
            previous_completed = all(
                j in attempt.completed_objectives for j in range(i)
            )
            if not previous_completed:
                # Skip this objective until previous ones are done
                continue
        
        # Check if objective is completed
        # Objectives can have different completion criteria
        obj_type = obj.get('type', 'command') if isinstance(obj, dict) else 'command'
        
        if obj_type == 'command':
            # Check if specific command was run
            required_cmd = obj.get('command', '').lower() if isinstance(obj, dict) else ''
            if required_cmd and parsed.command.lower() == required_cmd.lower():
                newly_completed.append(i)
        
        elif obj_type == 'output':
            # Check if output contains specific text
            required_text = obj.get('contains', '').lower() if isinstance(obj, dict) else ''
            if required_text and required_text in result.output.lower():
                newly_completed.append(i)
        
        elif obj_type == 'flag':
            # Check if any flag appears in the output
            for flag in flags:
                if flag.lower() in result.output.lower():
                    newly_completed.append(i)
                    break
    
    # Update completed objectives
    if newly_completed:
        attempt.completed_objectives = list(
            set(attempt.completed_objectives) | set(newly_completed)
        )
        
        # Check if all objectives completed (excluding flag-type for manual labs)
        non_flag_objectives = [o for o in objectives if (isinstance(o, dict) and o.get('type') != 'flag') or not isinstance(o, dict)]
        completed_count = sum(1 for i, o in enumerate(objectives) if i in attempt.completed_objectives)
        
        if completed_count >= len(objectives):
            attempt.completed = True
            attempt.completed_at = timezone.now()
            
            # Award XP if not already awarded
            if not attempt.xp_awarded:
                from progress.services import award_xp
                
                base_xp = attempt.lab.xp_reward
                if attempt.solution_viewed:
                    penalty = attempt.lab.xp_penalty_for_solution
                    base_xp = int(base_xp * (100 - penalty) / 100)
                
                award_xp(attempt.user, base_xp, f'Completed lab: {attempt.lab.title}')
                attempt.xp_awarded = True
        
        attempt.save()
    
    return newly_completed



@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def get_hint(request, lab_id):
    """Get the next hint for the lab."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    attempt = get_object_or_404(LabAttempt, user=request.user, lab=lab)
    
    hints = lab.hints or []
    
    if attempt.hints_used >= len(hints):
        return Response({
            'error': 'No more hints available.',
        }, status=status.HTTP_400_BAD_REQUEST)
    
    hint_index = attempt.hints_used
    hint_text = hints[hint_index]
    
    attempt.hints_used += 1
    attempt.save(update_fields=['hints_used'])
    
    return Response({
        'hint_number': hint_index + 1,
        'hint_text': hint_text,
        'hints_remaining': len(hints) - attempt.hints_used,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def submit_flag(request, lab_id):
    """Submit a flag for CTF-style challenges."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    attempt = get_object_or_404(LabAttempt, user=request.user, lab=lab)
    
    serializer = FlagSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    submitted_flag = serializer.validated_data['flag'].strip()
    flags = lab.flags or []
    
    # Check if flag is correct
    correct = submitted_flag in flags
    xp_earned = 0
    
    if correct and not attempt.completed:
        attempt.completed = True
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Award XP (with penalty if solution was viewed)
        if not attempt.xp_awarded:
            from progress.services import award_xp
            
            base_xp = lab.xp_reward
            if attempt.solution_viewed:
                penalty = lab.xp_penalty_for_solution
                base_xp = int(base_xp * (100 - penalty) / 100)
            
            award_xp(request.user, base_xp, f'Completed lab: {lab.title}')
            attempt.xp_awarded = True
            attempt.save(update_fields=['xp_awarded'])
            xp_earned = base_xp
    
    return Response({
        'correct': correct,
        'message': 'Congratulations! Flag accepted!' if correct else 'Incorrect flag. Try again.',
        'xp_awarded': xp_earned,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_lab_attempts(request):
    """Get user's lab attempts."""
    attempts = LabAttempt.objects.filter(
        user=request.user
    ).select_related('lab').order_by('-started_at')
    
    serializer = LabAttemptSerializer(attempts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def reset_lab(request, lab_id):
    """Reset a lab attempt."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    attempt = get_object_or_404(LabAttempt, user=request.user, lab=lab)
    
    # Clear simulator
    key = f"{request.user.id}_{lab_id}"
    if key in _simulators:
        del _simulators[key]
    
    # Reset attempt (keep hints_revealed and solution_viewed to prevent abuse)
    attempt.completed = False
    attempt.completed_at = None
    attempt.completed_objectives = []
    attempt.commands_executed = 0
    attempt.save()
    
    return Response({
        'message': 'Lab reset successfully.',
        'attempt': LabAttemptSerializer(attempt).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def solution_viewed(request, lab_id):
    """Mark that the user viewed the step-by-step solution."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    attempt = get_object_or_404(LabAttempt, user=request.user, lab=lab)
    
    if not attempt.solution_viewed:
        attempt.solution_viewed = True
        attempt.save(update_fields=['solution_viewed'])
    
    # Calculate reduced XP
    penalty = lab.xp_penalty_for_solution
    reduced_xp = int(lab.xp_reward * (100 - penalty) / 100)
    
    return Response({
        'solution_viewed': True,
        'original_xp': lab.xp_reward,
        'reduced_xp': reduced_xp,
        'penalty_percent': penalty,
    })

