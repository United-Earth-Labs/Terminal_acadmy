import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.vercel')
os.environ['DEBUG'] = 'False'

django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = 'admin@terminal.academy'
password = 'adminpassword'

if not User.objects.filter(email=email).exists():
    user = User.objects.create_superuser(email=email, password=password)
    print(f'Admin created: {email}')
else:
    print(f'Admin already exists: {email}')
