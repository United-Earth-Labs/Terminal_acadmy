import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from users.models import CustomUser

email = 'admin@terminal.academy'
password = 'adminpassword'

user, created = CustomUser.objects.get_or_create(
    email=email,
    defaults={
        'is_staff': True,
        'is_superuser': True,
        'skill_level': 'beginner'
    }
)

if created or not user.check_password(password):
    user.set_password(password)
    user.save()
    print(f"User {email} created/updated with password '{password}'")
else:
    print(f"User {email} already exists.")
