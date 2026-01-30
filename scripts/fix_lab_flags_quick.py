"""
Quick fix for lab filesystem flags.
Run with: python manage.py runscript fix_lab_flags (if django-extensions is installed)
Or run: python -c "exec(open('scripts/fix_lab_flags_quick.py').read())"
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from labs.models import Lab

def fix_lab_flags():
    """Update each lab's filesystem .secret.txt to contain the correct flag."""
    for lab in Lab.objects.filter(is_active=True).exclude(environment=None):
        if not lab.flags:
            print(f"  Skipping Lab {lab.id}: {lab.title} - no flags")
            continue
        
        env = lab.environment
        fs = env.filesystem or {}
        
        # Check if filesystem has .secret.txt
        secret_path = '/home/student/.secret.txt'
        if secret_path not in fs:
            print(f"  Skipping Lab {lab.id}: {lab.title} - no .secret.txt in filesystem")
            continue
        
        # Update secret file to contain the lab's expected flag
        first_flag = lab.flags[0]  # Use the first flag
        fs[secret_path]['content'] = f"""🎉 Congratulations! You found the secret file!

{first_flag}

Well done! You now know how to find hidden files in Linux.
"""
        env.filesystem = fs
        env.save(update_fields=['filesystem'])
        print(f"  Fixed Lab {lab.id}: {lab.title} -> {first_flag}")

if __name__ == '__main__':
    print("Syncing lab flags with filesystem secrets...")
    fix_lab_flags()
    print("\nDone! Remember to restart the server and reset labs to apply changes.")
