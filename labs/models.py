"""
Lab models for Terminal Academy.

This module contains models for terminal labs, simulated environments,
and user lab attempts.
"""
import json
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from courses.models import Lesson


class SimulatedEnvironment(models.Model):
    """
    Defines a simulated environment for labs.
    
    Contains configuration for file systems, network services,
    and expected command outputs.
    """
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    
    # Simulated file system (JSON)
    filesystem = models.JSONField(
        _('filesystem'),
        default=dict,
        help_text=_('JSON structure representing the simulated filesystem')
    )
    
    # Simulated network configuration
    network_config = models.JSONField(
        _('network config'),
        default=dict,
        help_text=_('Simulated network hosts, open ports, services')
    )
    
    # User info for the simulation
    simulated_user = models.CharField(
        _('simulated user'),
        max_length=50,
        default='student'
    )
    simulated_hostname = models.CharField(
        _('simulated hostname'),
        max_length=100,
        default='academy-lab'
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('simulated environment')
        verbose_name_plural = _('simulated environments')
    
    def __str__(self):
        return self.name


class Lab(models.Model):
    """
    A terminal lab assignment attached to a lesson.
    
    Labs provide hands-on practice with simulated command execution.
    """
    
    class Difficulty(models.TextChoices):
        EASY = 'easy', _('Easy')
        MEDIUM = 'medium', _('Medium')
        HARD = 'hard', _('Hard')
        EXPERT = 'expert', _('Expert')
    
    # Association
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='labs'
    )
    
    # Basic info
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    instructions = models.TextField(
        _('instructions'),
        help_text=_('Step-by-step instructions for the student')
    )
    
    # Difficulty and rewards
    difficulty = models.CharField(
        _('difficulty'),
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM
    )
    xp_reward = models.PositiveIntegerField(_('XP reward'), default=25)
    time_limit = models.PositiveIntegerField(
        _('time limit (minutes)'),
        null=True,
        blank=True
    )
    
    # Environment
    environment = models.ForeignKey(
        SimulatedEnvironment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='labs'
    )
    
    # Command configuration
    allowed_commands = models.JSONField(
        _('allowed commands'),
        default=list,
        help_text=_('Commands allowed in this lab (empty = use global whitelist)')
    )
    
    # Objectives (JSON list of objectives to complete)
    objectives = models.JSONField(
        _('objectives'),
        default=list,
        help_text=_('List of objectives the student must complete')
    )
    
    # Hints
    hints = models.JSONField(
        _('hints'),
        default=list,
        help_text=_('Hints that can be revealed progressively')
    )
    
    # Flags/answers for CTF-style labs
    flags = models.JSONField(
        _('flags'),
        default=list,
        help_text=_('Secret flags for CTF-style challenges')
    )
    
    # Step-by-step solution guide (shown when user fails/gives up)
    solution_guide = models.TextField(
        _('solution guide'),
        blank=True,
        help_text=_('Step-by-step teaching content shown when user needs help')
    )
    
    # XP penalty when solution is viewed
    xp_penalty_for_solution = models.PositiveIntegerField(
        _('XP penalty for viewing solution'),
        default=50,
        help_text=_('Percentage of XP to deduct if solution is viewed (0-100)')
    )
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('lab')
        verbose_name_plural = _('labs')
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"
    
    @property
    def objective_count(self):
        return len(self.objectives) if self.objectives else 0


class LabAttempt(models.Model):
    """
    Records a user's attempt at a lab.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_attempts'
    )
    lab = models.ForeignKey(
        Lab,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    # Status
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    completed = models.BooleanField(_('completed'), default=False)
    
    # Progress
    completed_objectives = models.JSONField(
        _('completed objectives'),
        default=list,
        help_text=_('Indices of completed objectives')
    )
    hints_used = models.PositiveIntegerField(_('hints used'), default=0)
    
    # Stats
    commands_executed = models.PositiveIntegerField(
        _('commands executed'),
        default=0
    )
    
    # Track which hints were revealed
    hints_revealed = models.JSONField(
        _('hints revealed'),
        default=list,
        help_text=_('Indices of hints that have been revealed')
    )
    
    # Track if solution was viewed
    solution_viewed = models.BooleanField(
        _('solution viewed'),
        default=False,
        help_text=_('User viewed the step-by-step solution')
    )
    
    # XP tracking
    xp_awarded = models.BooleanField(_('XP awarded'), default=False)
    
    class Meta:
        verbose_name = _('lab attempt')
        verbose_name_plural = _('lab attempts')
        unique_together = ['user', 'lab']
    
    def __str__(self):
        status = '✓' if self.completed else '○'
        return f"{status} {self.user.email} - {self.lab.title}"
    
    @property
    def progress_percentage(self):
        if not self.lab.objectives:
            return 0
        return int(len(self.completed_objectives) / len(self.lab.objectives) * 100)


class CommandLog(models.Model):
    """
    Logs commands executed by users in labs for security auditing.
    """
    
    attempt = models.ForeignKey(
        LabAttempt,
        on_delete=models.CASCADE,
        related_name='command_logs'
    )
    
    command = models.CharField(_('command'), max_length=1000)
    output = models.TextField(_('output'), blank=True)
    
    # Security tracking
    was_blocked = models.BooleanField(_('was blocked'), default=False)
    blocked_reason = models.CharField(
        _('blocked reason'),
        max_length=200,
        blank=True
    )
    
    executed_at = models.DateTimeField(_('executed at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('command log')
        verbose_name_plural = _('command logs')
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.attempt.user.email}: {self.command[:50]}"
