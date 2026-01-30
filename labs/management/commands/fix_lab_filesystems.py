"""
Management command to fix lab environments with empty filesystems.

This populates any SimulatedEnvironment objects that have empty or missing
filesystem configurations with the default filesystem.
"""
from django.core.management.base import BaseCommand
from labs.models import SimulatedEnvironment


# Default filesystem structure - matches simulator.py
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


class Command(BaseCommand):
    help = 'Fix lab environments with missing /home/student paths in their filesystems'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all environments
        environments = SimulatedEnvironment.objects.all()
        fixed_count = 0
        
        self.stdout.write(f"Checking {environments.count()} simulated environments...")
        
        for env in environments:
            fs = env.filesystem or {}
            
            # Check if /home/student exists - this is required for commands to work
            if '/home/student' not in fs:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"Would fix: {env.name} (ID: {env.id}) - missing /home/student path")
                    )
                else:
                    # Merge default filesystem with any existing custom paths
                    merged_fs = {**DEFAULT_FILESYSTEM}
                    for path, node in fs.items():
                        if path not in merged_fs:
                            merged_fs[path] = node
                    
                    env.filesystem = merged_fs
                    env.save(update_fields=['filesystem'])
                    self.stdout.write(
                        self.style.SUCCESS(f"Fixed: {env.name} (ID: {env.id}) - added {len(merged_fs)} filesystem entries")
                    )
                fixed_count += 1
            else:
                self.stdout.write(f"  OK: {env.name} (ID: {env.id})")
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS("\n✓ All environments have valid /home/student path!"))
        else:
            if dry_run:
                self.stdout.write(self.style.WARNING(f"\n{fixed_count} environment(s) would be fixed. Run without --dry-run to apply."))
            else:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Fixed {fixed_count} environment(s)!"))
                self.stdout.write(self.style.WARNING(
                    "\n⚠️  IMPORTANT: Restart the Django server to clear cached simulators."
                ))
                self.stdout.write(self.style.WARNING(
                    "   Users may also need to click 'Reset Lab' in their browser."
                ))
