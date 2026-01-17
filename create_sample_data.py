"""Run this script to create sample data."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils.text import slugify
from courses.models import Category, Course, Module, Lesson
from labs.models import Lab, SimulatedEnvironment
from progress.models import Achievement

print('Creating sample content...')

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

print('✓ Categories created')

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

# Create module for Linux course
linux_module, _ = Module.objects.get_or_create(
    course=linux_course,
    title='Basic Commands',
    defaults={
        'description': 'Learn essential Linux commands',
        'order': 1,
    }
)

# Create lesson for Linux
linux_lesson, _ = Lesson.objects.get_or_create(
    module=linux_module,
    slug='file-navigation',
    defaults={
        'title': 'File Navigation',
        'content': 'Learn ls, cd, pwd, cat and more.',
        'content_type': 'interactive',
        'order': 1,
        'estimated_duration': 15,
    }
)

print('✓ Linux course created')

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
    title='Reconnaissance',
    defaults={
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
        'content_type': 'interactive',
        'order': 1,
        'estimated_duration': 20,
    }
)

print('✓ Web Security course created')

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

print('✓ Simulated environment created')

# Create the main challenge lab
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
        "You need a tool to discover what services are running on a remote server...",
        "Network scanning tools can reveal open ports. There's a famous one that starts with 'n'...",
        "The nmap command can scan for open ports. You need to specify the target IP address.",
        "Use: nmap 192.168.1.100 - then look for database-related services in the output.",
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
The flag format is FLAG{service_port}, so submit:
```
FLAG{mysql_3306}
```

### What You Learned
- nmap is a powerful network scanning tool
- Different services run on different ports
- MySQL typically runs on port 3306
""",
    xp_penalty_for_solution=50,
    is_active=True,
)

print('✓ Network Recon Challenge created')

# Create beginner lab
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
        "What command lets you see what's inside a folder?",
        "In Linux, there's a short command to 'list' directory contents...",
        "Some files are hidden! Hidden files start with a dot (.). Try adding flags to your list command.",
        "The 'ls' command with '-la' flag shows ALL files including hidden ones.",
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
- ls lists files
- ls -la shows hidden files
- cat displays file contents
""",
    xp_penalty_for_solution=50,
    is_active=True,
)

print('✓ Linux File Explorer lab created')

# Create achievements
achievements_data = [
    ('First Steps', 'Complete your first lesson', 'first_steps', 10),
    ('Terminal Novice', 'Execute 100 commands', 'terminal_100', 25),
    ('Flag Hunter', 'Capture your first flag', 'first_flag', 50),
    ('Perfect Student', 'Complete a lab without hints', 'no_hints', 75),
    ('Security Master', 'Complete all beginner labs', 'beginner_complete', 100),
]

for name, desc, slug, xp in achievements_data:
    Achievement.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name,
            'description': desc,
            'xp_reward': xp,
            'category': 'general',
        }
    )

print('✓ Achievements created')
print('\n✅ All sample content created!')
print('Visit /courses/ to see courses')
print('Visit /labs/ to try challenges')
