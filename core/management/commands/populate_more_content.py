"""
Django management command to add MORE sample content.

Usage:
    python manage.py populate_more_content
"""
from django.core.management.base import BaseCommand
from courses.models import Course, Module, Lesson
from labs.models import Lab, SimulatedEnvironment


class Command(BaseCommand):
    help = 'Adds more courses, labs, and lessons to the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding more content...'))
        
        # Add more to Linux Fundamentals
        self.expand_linux_course()
        
        # Add more to Web Security
        self.expand_web_security()
        
        # Create Network Fundamentals course
        self.create_network_course()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Additional content created!'))
        self.stdout.write(f'Total courses: {Course.objects.count()}')
        self.stdout.write(f'Total modules: {Module.objects.count()}')
        self.stdout.write(f'Total lessons: {Lesson.objects.count()}')
        self.stdout.write(f'Total labs: {Lab.objects.count()}')

    def expand_linux_course(self):
        self.stdout.write('Expanding Linux Fundamentals...')
        
        course = Course.objects.get(slug='linux-fundamentals')
        
        # Module 2: File Management
        module2, _ = Module.objects.get_or_create(
            course=course,
            title='File Management',
            defaults={'order': 2, 'description': 'Working with files and directories'}
        )
        
        lesson2, _ = Lesson.objects.get_or_create(
            module=module2,
            title='File Permissions',
            defaults={
                'order': 1,
                'content': '''# File Permissions in Linux

Every file in Linux has permissions that control who can read, write, or execute it.

## Permission Types

- **r (read)** - View file contents
- **w (write)** - Modify file
- **x (execute)** - Run as program

## Permission Groups

- **Owner** - The user who owns the file
- **Group** - Users in the file's group
- **Others** - Everyone else

## Reading Permissions

Use `ls -l` to see permissions:
```
-rw-r--r-- 1 user group 1234 Jan 18 12:00 file.txt
```

This breaks down as:
- `-` = file type (- for file, d for directory)
- `rw-` = owner can read and write
- `r--` = group can only read
- `r--` = others can only read

Let's practice in the lab!''',
                'content_type': 'text',
                'xp_reward': 75,
                'estimated_duration': 15
            }
        )
        
        # Create environment for permissions lab
        env2, _ = SimulatedEnvironment.objects.get_or_create(
            name='File Permissions Environment',
            defaults={
                'description': 'Environment for learning file permissions',
                'filesystem': {
                    '/home/student/': {
                        'public.txt': 'This file is readable by everyone.',
                        'private.txt': 'This file should be private.',
                        'secret_key.txt': 'FLAG{permission_master}',
                        'script.sh': '#!/bin/bash\necho "Hello World"'
                    }
                },
                'simulated_user': 'student',
                'simulated_hostname': 'linux-lab'
            }
        )
        
        # LAB 2: File Permissions
        Lab.objects.get_or_create(
            lesson=lesson2,
            title='Understanding File Permissions',
            defaults={
                'description': 'Learn to read and modify file permissions.',
                'instructions': '''## Objectives

1. List files with detailed permissions
2. Identify which files are executable
3. Find files with insecure permissions
4. Locate the hidden flag

## Commands You'll Need

- `ls -l` - List files with permissions
- `ls -la` - List ALL files (including hidden)
- `chmod` - Change file permissions

**Hint**: Look for files that everyone can read!''',
                'difficulty': 'easy',
                'xp_reward': 125,
                'time_limit': 20,
                'environment': env2,
                'objectives': [
                    {'id': 1, 'description': 'List files with permissions', 'command': 'ls -l'},
                    {'id': 2, 'description': 'Find executable files', 'command': 'ls -l'},
                    {'id': 3, 'description': 'Read the secret key', 'command': 'cat secret_key.txt'}
                ],
                'hints': [
                    'Use ls -l to see file permissions',
                    'Files with x permission can be executed',
                    'The flag is in a file with "secret" in the name'
                ],
                'flags': ['FLAG{permission_master}'],
                'solution_guide': '''### Solution

1. **List all files with permissions**:
   ```
   ls -l
   ```

2. **Look for the secret file**:
   ```
   cat secret_key.txt
   ```
   
   Flag: `FLAG{permission_master}`

Great job! You understand Linux file permissions!''',
                'xp_penalty_for_solution': 30
            }
        )
        
        # Lesson 3: Finding Files
        lesson3, _ = Lesson.objects.get_or_create(
            module=module2,
            title='Finding Sensitive Data',
            defaults={
                'order': 2,
                'content': '''# Finding Files and Data

As a security professional, you often need to search for sensitive information in systems.

## Essential Commands

### `find` - Search for files
```bash
find /path -name "*.txt"  # Find all .txt files
find . -type f            # Find all files
find . -type d            # Find all directories
```

### `grep` - Search inside files
```bash
grep "password" file.txt  # Search for "password"
grep -r "API_KEY" .       # Recursively search directory
grep -i "secret" *        # Case-insensitive search
```

### `locate` - Fast file search (uses database)
```bash
locate passwords.txt
```

## Real-World Use Cases

- Finding configuration files with credentials
- Locating log files
- Discovering sensitive data leaks
- Forensic investigations

Let's hunt for sensitive data!''',
                'content_type': 'text',
                'xp_reward': 100,
                'estimated_duration': 20
            }
        )
        
        # Environment for finding files
        env3, _ = SimulatedEnvironment.objects.get_or_create(
            name='Data Discovery Environment',
            defaults={
                'description': 'Environment with hidden sensitive files',
                'filesystem': {
                    '/home/student/': {
                        'readme.txt': 'Welcome! Some files are hidden.',
                        'documents/': {
                            'report.txt': 'Annual report 2024',
                            'passwords.txt': 'admin:admin123\nuser:password\nFLAG{grep_master}'
                        },
                        '.hidden/': {
                            'config.txt': 'API_KEY=secret123'
                        }
                    }
                },
                'simulated_user': 'student',
                'simulated_hostname': 'linux-lab'
            }
        )
        
        # LAB 3: Finding Sensitive Data
        Lab.objects.get_or_create(
            lesson=lesson3,
            title='Hunt for Sensitive Files',
            defaults={
                'description': 'Practice finding files with grep and find commands.',
                'instructions': '''## Mission

You've gained access to a system. Your job is to find all sensitive files containing passwords or API keys.

## Objectives

1. List all directories
2. Find the passwords.txt file
3. Search for files containing "FLAG"
4. Extract the flag

## Commands You'll Need

- `ls -la` - List all files (including hidden)
- `find . -name "*.txt"` - Find text files
- `grep -r "FLAG" .` - Search for FLAG in all files
- `cat filename` - Read file

**Tip**: Some files might be in subdirectories!''',
                'difficulty': 'easy',
                'xp_reward': 150,
                'time_limit': 25,
                'environment': env3,
                'objectives': [
                    {'id': 1, 'description': 'List all files including hidden', 'command': 'ls -la'},
                    {'id': 2, 'description': 'Find passwords.txt', 'command': 'find . -name passwords.txt'},
                    {'id': 3, 'description': 'Get the flag', 'command': 'grep -r FLAG .'}
                ],
                'hints': [
                    'Use find to locate files by name',
                    'grep -r searches recursively through directories',
                    'The flag is in a file named passwords.txt in a subdirectory'
                ],
                'flags': ['FLAG{grep_master}'],
                'solution_guide': '''### Solution

1. **Find all text files**:
   ```
   find . -name "*.txt"
   ```

2. **Search for FLAG**:
   ```
   grep -r "FLAG" .
   ```
   
   Or directly:
   ```
   cat documents/passwords.txt
   ```

Flag: `FLAG{grep_master}`

Excellent! You can now find sensitive data like a pro!''',
                'xp_penalty_for_solution': 35
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Linux Fundamentals expanded'))

    def expand_web_security(self):
        self.stdout.write('Expanding Web Security...')
        
        course = Course.objects.get(slug='web-security')
        
        # Module 2: Injection Attacks
        module2, _ = Module.objects.get_or_create(
            course=course,
            title='Injection Attacks',
            defaults={'order': 2, 'description': 'SQL Injection and Command Injection'}
        )
        
        lesson, _ = Lesson.objects.get_or_create(
            module=module2,
            title='SQL Injection Basics',
            defaults={
                'order': 1,
                'content': '''# SQL Injection (SQLi)

SQL Injection is one of the most critical web vulnerabilities. It allows attackers to execute arbitrary SQL queries.

## How It Works

Vulnerable code:
```python
username = request.POST['username']
query = f"SELECT * FROM users WHERE username='{username}'"
```

Attacker input: `admin' OR '1'='1`

Resulting query:
```sql
SELECT * FROM users WHERE username='admin' OR '1'='1'
```

Since `'1'='1'` is always true, this bypasses authentication!

## Common Targets

- Login forms
- Search functions
- URL parameters
- Any user input used in SQL queries

## Prevention

✅ **Use parameterized queries**
✅ **Input validation**
✅ **Least privilege database access**
❌ **Never trust user input**

Let's exploit this in a safe environment!''',
                'content_type': 'text',
                'xp_reward': 100,
                'estimated_duration': 25
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Web Security expanded'))

    def create_network_course(self):
        self.stdout.write('Creating Network Fundamentals...')
        
        course, created = Course.objects.get_or_create(
            slug='network-fundamentals',
            defaults={
                'title': 'Network Fundamentals',
                'description': 'Learn networking basics, reconnaissance, and scanning techniques. Perfect for aspiring penetration testers!',
                'level': 'intermediate',
                'status': 'published'
            }
        )
        
        if created:
            # Module 1
            module1, _ = Module.objects.get_or_create(
                course=course,
                title='Networking Basics',
                defaults={'order': 1, 'description': 'Understanding networks and protocols'}
            )
            
            lesson1, _ = Lesson.objects.get_or_create(
                module=module1,
                title='TCP/IP and Common Ports',
                defaults={
                    'order': 1,
                    'content': '''# TCP/IP and Network Ports

Understanding network protocols and ports is essential for security testing.

## Common Ports

- **22** - SSH (Secure Shell)
- **80** - HTTP (Web)
- **443** - HTTPS (Secure Web)
- **21** - FTP (File Transfer)
- **3306** - MySQL Database
- **3389** - RDP (Remote Desktop)

## Network Commands

- `ping` - Test connectivity
- `netstat` - Show network connections
- `curl` - Transfer data from URLs

## Reconnaissance

In ethical hacking, we gather information about targets:
- What services are running?
- Which ports are open?
- What versions are they?

This is called **reconnaissance** or **enumeration**.

Ready to scan your first target?''',
                    'content_type': 'text',
                    'xp_reward': 100,
                    'estimated_duration': 20
                }
            )
            
            self.stdout.write(self.style.SUCCESS('  ✓ Network Fundamentals created'))
        else:
            self.stdout.write('  ℹ Network Fundamentals already exists')
