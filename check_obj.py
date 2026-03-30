import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from labs.models import Lab
import json

lab = Lab.objects.get(title='JSX Superpowers')
with open('temp_objectives.json', 'w') as f:
    json.dump(lab.objectives, f, indent=2)
