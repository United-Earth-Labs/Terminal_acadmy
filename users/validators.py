"""
Password validators for Terminal Academy.

These validators ensure password complexity and security.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """
    Validate that the password meets complexity requirements:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    
    def __init__(self, min_uppercase=1, min_lowercase=1, min_digits=1, min_special=1):
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special
    
    def validate(self, password, user=None):
        errors = []
        
        if len(re.findall(r'[A-Z]', password)) < self.min_uppercase:
            errors.append(
                ValidationError(
                    _('Password must contain at least %(min)d uppercase letter(s).'),
                    code='password_no_uppercase',
                    params={'min': self.min_uppercase},
                )
            )
        
        if len(re.findall(r'[a-z]', password)) < self.min_lowercase:
            errors.append(
                ValidationError(
                    _('Password must contain at least %(min)d lowercase letter(s).'),
                    code='password_no_lowercase',
                    params={'min': self.min_lowercase},
                )
            )
        
        if len(re.findall(r'\d', password)) < self.min_digits:
            errors.append(
                ValidationError(
                    _('Password must contain at least %(min)d digit(s).'),
                    code='password_no_digit',
                    params={'min': self.min_digits},
                )
            )
        
        special_chars = re.findall(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password)
        if len(special_chars) < self.min_special:
            errors.append(
                ValidationError(
                    _('Password must contain at least %(min)d special character(s).'),
                    code='password_no_special',
                    params={'min': self.min_special},
                )
            )
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            'Your password must contain at least '
            '%(uppercase)d uppercase letter(s), '
            '%(lowercase)d lowercase letter(s), '
            '%(digits)d digit(s), and '
            '%(special)d special character(s).'
        ) % {
            'uppercase': self.min_uppercase,
            'lowercase': self.min_lowercase,
            'digits': self.min_digits,
            'special': self.min_special,
        }


class NoCommonPatternsValidator:
    """
    Validate that the password doesn't contain common patterns.
    """
    
    common_patterns = [
        r'123456',
        r'password',
        r'qwerty',
        r'abc123',
        r'letmein',
        r'welcome',
        r'admin',
        r'login',
    ]
    
    def validate(self, password, user=None):
        password_lower = password.lower()
        
        for pattern in self.common_patterns:
            if pattern in password_lower:
                raise ValidationError(
                    _('Password contains a common pattern that is not allowed.'),
                    code='password_common_pattern',
                )
    
    def get_help_text(self):
        return _('Your password cannot contain common patterns like "password" or "123456".')
