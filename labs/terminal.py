"""
Terminal command parser for Terminal Academy.

This module provides safe command parsing with whitelisting,
input sanitization, and security validation.

SECURITY CRITICAL: No real system commands are ever executed.
All output is simulated.
"""
import re
import shlex
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass

from django.conf import settings


@dataclass
class ParsedCommand:
    """Represents a parsed terminal command."""
    command: str
    args: List[str]
    raw_input: str
    is_valid: bool
    error_message: str = ''


class CommandParser:
    """
    Parses and validates terminal commands.
    
    This parser ensures only whitelisted commands are accepted
    and blocks potentially dangerous patterns.
    """
    
    def __init__(self, allowed_commands: List[str] = None):
        """
        Initialize the parser.
        
        Args:
            allowed_commands: List of allowed commands. If None, uses global whitelist.
        """
        self.allowed_commands = allowed_commands or settings.LAB_WHITELISTED_COMMANDS
        self.blocked_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in settings.LAB_BLOCKED_PATTERNS
        ]
    
    def parse(self, user_input: str) -> ParsedCommand:
        """
        Parse a user command input.
        
        Args:
            user_input: The raw command string from the user.
        
        Returns:
            ParsedCommand object with validation results.
        """
        # Clean the input
        user_input = user_input.strip()
        
        if not user_input:
            return ParsedCommand(
                command='',
                args=[],
                raw_input=user_input,
                is_valid=False,
                error_message='Empty command'
            )
        
        # Check for blocked patterns first
        blocked, reason = self._check_blocked_patterns(user_input)
        if blocked:
            return ParsedCommand(
                command='',
                args=[],
                raw_input=user_input,
                is_valid=False,
                error_message=f'Command blocked: {reason}'
            )
        
        # Parse the command
        try:
            parts = shlex.split(user_input)
        except ValueError as e:
            return ParsedCommand(
                command='',
                args=[],
                raw_input=user_input,
                is_valid=False,
                error_message=f'Invalid command syntax: {str(e)}'
            )
        
        if not parts:
            return ParsedCommand(
                command='',
                args=[],
                raw_input=user_input,
                is_valid=False,
                error_message='Empty command'
            )
        
        command = parts[0].lower()
        args = parts[1:]
        
        # Check if command is allowed
        if command not in self.allowed_commands:
            return ParsedCommand(
                command=command,
                args=args,
                raw_input=user_input,
                is_valid=False,
                error_message=f'Command not allowed: {command}'
            )
        
        return ParsedCommand(
            command=command,
            args=args,
            raw_input=user_input,
            is_valid=True
        )
    
    def _check_blocked_patterns(self, user_input: str) -> Tuple[bool, str]:
        """
        Check if the input matches any blocked patterns.
        
        Returns:
            Tuple of (is_blocked, reason)
        """
        for pattern in self.blocked_patterns:
            if pattern.search(user_input):
                return True, 'Dangerous pattern detected'
        
        # Additional security checks
        dangerous_chars = ['&&', '||', ';', '`', '$(',  '$(', '|']
        for char in dangerous_chars:
            if char in user_input:
                return True, 'Shell metacharacters not allowed'
        
        # Check for path traversal
        if '../' in user_input or '..\\' in user_input:
            return True, 'Path traversal not allowed'
        
        return False, ''
    
    def get_help(self) -> str:
        """Get help text showing available commands."""
        return "Available commands:\n" + "\n".join(
            f"  {cmd}" for cmd in sorted(self.allowed_commands)
        )


class InputSanitizer:
    """Sanitizes user input for safety."""
    
    @staticmethod
    def sanitize(user_input: str, max_length: int = 500) -> str:
        """
        Sanitize user input.
        
        Args:
            user_input: The raw input string
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not user_input:
            return ''
        
        # Limit length
        user_input = user_input[:max_length]
        
        # Remove null bytes
        user_input = user_input.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        user_input = ''.join(
            char for char in user_input 
            if char.isprintable() or char in '\n\t'
        )
        
        return user_input.strip()
    
    @staticmethod
    def sanitize_for_display(text: str) -> str:
        """Sanitize text for HTML display (prevent XSS)."""
        import html
        return html.escape(text)
