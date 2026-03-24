"""
Management command to create sample challenges with adaptive learning content.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from courses.models import Category, Course, Module, Lesson
from labs.models import Lab, SimulatedEnvironment
from progress.models import Achievement


class Command(BaseCommand):
    help = 'Create sample courses, labs, and achievements for demo'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample content...')
        
        # Create categories
        security_cat, _ = Category.objects.get_or_create(
            name='Cybersecurity',
            defaults={
                'slug': 'cybersecurity',
                'description': 'Ethical hacking and security courses',
            }
        )
        
        linux_cat, _ = Category.objects.get_or_create(
            name='Linux',
            defaults={
                'slug': 'linux',
                'description': 'Linux system administration',
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Categories created'))
        
        # Create Linux course
        linux_course, _ = Course.objects.get_or_create(
            slug='linux-fundamentals',
            defaults={
                'title': 'Linux Fundamentals',
                'short_description': 'Master the command line',
                'description': 'Learn essential Linux commands for ethical hacking.',
                'category': linux_cat,
                'level': 'beginner',
                'status': 'published',
                'xp_reward': 200,
                'estimated_duration': 120,
            }
        )
        
        # Create module and lesson for Linux course
        linux_module, _ = Module.objects.get_or_create(
            course=linux_course,
            slug='basic-commands',
            defaults={
                'title': 'Basic Commands',
                'description': 'Learn essential Linux commands',
                'order': 1,
            }
        )
        
        linux_lesson, _ = Lesson.objects.get_or_create(
            module=linux_module,
            slug='file-navigation',
            defaults={
                'title': 'File Navigation',
                'content': 'Learn ls, cd, pwd, cat and more.',
                'lesson_type': 'practice',
                'order': 1,
                'estimated_minutes': 15,
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Linux course created'))
        
        # Create Web Security course  
        web_course, _ = Course.objects.get_or_create(
            slug='web-security-basics',
            defaults={
                'title': 'Web Security Basics',
                'short_description': 'Learn web application security',
                'description': 'Understand common vulnerabilities and how to find them.',
                'category': security_cat,
                'level': 'intermediate',
                'status': 'published',
                'xp_reward': 350,
                'estimated_duration': 180,
            }
        )
        
        web_module, _ = Module.objects.get_or_create(
            course=web_course,
            slug='reconnaissance',
            defaults={
                'title': 'Reconnaissance',
                'description': 'Information gathering techniques',
                'order': 1,
            }
        )
        
        web_lesson, _ = Lesson.objects.get_or_create(
            module=web_module,
            slug='port-scanning',
            defaults={
                'title': 'Port Scanning',
                'content': 'Learn network reconnaissance with nmap.',
                'lesson_type': 'practice',
                'order': 1,
                'estimated_minutes': 20,
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Web Security course created'))
        
        # Create simulated environment
        network_env, _ = SimulatedEnvironment.objects.get_or_create(
            name='Web Server Target',
            defaults={
                'description': 'Simulated web server for scanning',
                'simulated_user': 'student',
                'simulated_hostname': 'academy-lab',
                'filesystem': {
                    '/': {'type': 'dir'},
                    '/home': {'type': 'dir'},
                    '/home/student': {'type': 'dir'},
                    '/home/student/notes.txt': {
                        'type': 'file',
                        'content': 'Target: 192.168.1.100\nHint: Check open ports!'
                    },
                },
                'network_config': {
                    'hosts': {
                        '192.168.1.100': {
                            'hostname': 'target-server',
                            'ports': {
                                '22': {'service': 'ssh', 'banner': 'OpenSSH 8.2'},
                                '80': {'service': 'http', 'banner': 'Apache 2.4'},
                                '443': {'service': 'https', 'banner': 'Apache 2.4'},
                                '3306': {'service': 'mysql', 'banner': 'MySQL 8.0'},
                            }
                        }
                    }
                }
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Simulated environment created'))
        
        # Create the main challenge lab with adaptive learning
        Lab.objects.filter(title='Network Reconnaissance Challenge').delete()
        
        challenge_lab = Lab.objects.create(
            lesson=web_lesson,
            title='Network Reconnaissance Challenge',
            description='Your mission: Find all open ports on the target server (192.168.1.100) and identify the MySQL service.',
            instructions='A target server has been set up for you to practice. Find the flag by discovering what services are running.',
            difficulty='medium',
            xp_reward=50,
            time_limit=30,
            environment=network_env,
            objectives=[
                {'description': 'Scan the target for open ports', 'type': 'command', 'command': 'nmap'},
                {'description': 'Find the MySQL port', 'type': 'output', 'contains': '3306'},
                {'description': 'Submit the flag', 'type': 'flag'},
            ],
            hints=[
                "Try using the 'nmap' command to scan for open ports.",
                "The syntax is: nmap <target-ip>",
                "Look for a database service running on a common port (hint: 3306 is MySQL's default port).",
                "The flag format is FLAG{service_port} - for example: FLAG{mysql_3306}",
            ],
            flags=['FLAG{mysql_3306}', 'FLAG{MYSQL_3306}'],
            solution_guide="""## Step-by-Step Solution

### Step 1: Understand the Goal
You need to find what services are running on the target server at 192.168.1.100.

### Step 2: Use nmap to Scan
Run this command to scan for open ports:
```
nmap 192.168.1.100
```

### Step 3: Analyze the Results
You'll see output like:
```
PORT     STATE  SERVICE
22/tcp   open   ssh
80/tcp   open   http
443/tcp  open   https
3306/tcp open   mysql
```

### Step 4: Identify the MySQL Service
Notice that port 3306 is open and running MySQL.

### Step 5: Submit the Flag
The flag format is `FLAG{service_port}`, so submit:
```
FLAG{mysql_3306}
```

### What You Learned
- nmap is a powerful network scanning tool
- Different services run on different ports
- MySQL typically runs on port 3306
- Always get permission before scanning networks!
""",
            xp_penalty_for_solution=50,
            is_active=True,
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Network Recon Challenge created'))
        
        # Create a simpler beginner lab
        Lab.objects.filter(title='Linux File Explorer').delete()
        
        beginner_lab = Lab.objects.create(
            lesson=linux_lesson,
            title='Linux File Explorer',
            description='Navigate the Linux filesystem and find the hidden secret.',
            instructions='Use basic Linux commands to explore and find a secret file.',
            difficulty='easy',
            xp_reward=25,
            time_limit=15,
            objectives=[
                {'description': 'List files in current directory', 'type': 'command', 'command': 'ls'},
                {'description': 'Find the secret file', 'type': 'output', 'contains': 'secret'},
            ],
            hints=[
                "Try 'ls' to see what files are here",
                "Use 'ls -la' to show hidden files (starting with .)",
                "Use 'cat filename' to read a file's contents",
            ],
            flags=['FLAG{found_it}'],
            solution_guide="""## Step-by-Step Solution

### Step 1: List Files
Start by seeing what's in the current directory:
```
ls -la
```

### Step 2: Look for Hidden Files
Hidden files start with a dot (.)
You might see `.secret.txt`

### Step 3: Read the File
```
cat .secret.txt
```

### What You Learned
- `ls` lists files
- `ls -la` shows hidden files
- `cat` displays file contents
""",
            xp_penalty_for_solution=50,
            is_active=True,
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Linux File Explorer lab created'))
        
        # Create achievements
        achievements_data = [
            ('First Steps', 'Complete your first lesson', 'first_steps', 10, '🎯'),
            ('Terminal Novice', 'Execute 100 commands', 'terminal_100', 25, '💻'),
            ('Flag Hunter', 'Capture your first flag', 'first_flag', 50, '🚩'),
            ('Perfect Student', 'Complete a lab without hints', 'no_hints', 75, '⭐'),
            ('Security Master', 'Complete all beginner labs', 'beginner_complete', 100, '🏆'),
        ]
        
        for name, desc, slug, xp, icon in achievements_data:
            Achievement.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'xp_reward': xp,
                    'category': 'general',
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Achievements created'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All sample content created!'))
        self.stdout.write('You can now:\n')
        self.stdout.write('  - Visit /courses/ to see courses')
        self.stdout.write('  - Visit /labs/ to try the challenges')
        self.stdout.write('  - Visit /achievements/ to see achievements')
