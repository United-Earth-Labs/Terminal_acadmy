"""
Script to fix lab environments with incomplete filesystems.
Run this with: python scripts/fix_all_lab_filesystems.py
"""
import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from labs.models import SimulatedEnvironment


# Default filesystem structure that must exist for commands to work
DEFAULT_FILESYSTEM = {
    '/': {'type': 'dir', 'children': ['home', 'etc', 'var', 'tmp']},
    '/home': {'type': 'dir', 'children': ['student']},
    '/home/student': {
        'type': 'dir',
        'children': ['welcome.txt', 'notes.txt', 'scan_results', 'tools', '.secret.txt', '.bashrc']
    },
    '/home/student/welcome.txt': {
        'type': 'file',
        'content': 'Welcome to Terminal Academy!\n\nThis is your first Linux lab environment.\nUse basic commands to explore and complete the objectives.\n\nGood luck!\n'
    },
    '/home/student/notes.txt': {
        'type': 'file',
        'content': 'Welcome to Terminal Academy!\n\nYour first task is to explore this system.\nHint: Hidden files start with a dot (.)\n'
    },
    '/home/student/.secret.txt': {
        'type': 'file',
        'content': '🎉 Congratulations! You found the secret file!\n\nFLAG{found_it}\n\nWell done! You now know how to find hidden files in Linux.\n'
    },
    '/home/student/.bashrc': {
        'type': 'file',
        'content': '# .bashrc\n# User specific aliases and functions\nalias ll="ls -la"\n'
    },
    '/home/student/scan_results': {
        'type': 'dir',
        'children': ['target_192.168.1.100.txt']
    },
    '/home/student/scan_results/target_192.168.1.100.txt': {
        'type': 'file',
        'content': 'Scan completed at 2024-01-15\nOpen ports: 22, 80, 443, 3306\nServices: ssh, http, https, mysql\n'
    },
    '/home/student/tools': {'type': 'dir', 'children': []},
    '/etc': {'type': 'dir', 'children': ['passwd', 'hosts']},
    '/etc/passwd': {
        'type': 'file',
        'content': 'root:x:0:0:root:/root:/bin/bash\nstudent:x:1000:1000:Student:/home/student:/bin/bash\n'
    },
    '/etc/hosts': {
        'type': 'file',
        'content': '127.0.0.1    localhost\n192.168.1.100    target\n192.168.1.1    gateway\n'
    },
    '/var': {'type': 'dir', 'children': ['log']},
    '/var/log': {'type': 'dir', 'children': ['auth.log', 'syslog']},
    '/var/log/auth.log': {
        'type': 'file',
        'content': 'Jan 15 10:00:00 academy-lab sshd[1234]: Failed password for admin from 192.168.1.50\n'
    },
    '/tmp': {'type': 'dir', 'children': []},
}


def fix_environments():
    """Fix all environments that don't have /home/student in their filesystem."""
    environments = SimulatedEnvironment.objects.all()
    fixed_count = 0
    
    print(f"Checking {environments.count()} simulated environments...")
    
    for env in environments:
        fs = env.filesystem or {}
        
        # Check if /home/student exists in the filesystem
        if '/home/student' not in fs:
            print(f"  Fixing: {env.name} (ID: {env.id}) - missing /home/student")
            
            # Merge the default filesystem with any existing custom paths
            merged_fs = {**DEFAULT_FILESYSTEM}
            
            # Keep any custom paths that were already defined
            for path, node in fs.items():
                if path not in merged_fs:
                    merged_fs[path] = node
            
            env.filesystem = merged_fs
            env.save(update_fields=['filesystem'])
            fixed_count += 1
            print(f"    ✓ Fixed with {len(merged_fs)} filesystem entries")
        else:
            print(f"  OK: {env.name} (ID: {env.id})")
    
    if fixed_count == 0:
        print("\n✓ All environments already have valid filesystems!")
    else:
        print(f"\n✓ Fixed {fixed_count} environment(s)")
        print("\n⚠️  IMPORTANT: You should restart the Django server to clear cached simulators.")
        print("   Users may also need to click 'Reset Lab' to get the updated environment.")


if __name__ == '__main__':
    fix_environments()
