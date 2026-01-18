"""
Django management command to populate sample content for Terminal Academy.

Usage:
    python manage.py populate_content
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson
from labs.models import Lab, SimulatedEnvironment
from progress.models import Achievement

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with sample courses, labs, and achievements'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting content population...'))
        
        # Create Course 1: Linux Fundamentals
        self.create_linux_fundamentals()
        
        # Create Course 2: Web Security Basics
        self.create_web_security()
        
        # Create Achievements
        self.create_achievements()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Content population complete!'))
        self.stdout.write('Created:')
        self.stdout.write(f'  - {Course.objects.count()} courses')
        self.stdout.write(f'  - {Module.objects.count()} modules')
        self.stdout.write(f'  - {Lesson.objects.count()} lessons')
        self.stdout.write(f'  - {Lab.objects.count()} labs')
        self.stdout.write(f'  - {Achievement.objects.count()} achievements')

    def create_linux_fundamentals(self):
        self.stdout.write('Creating Linux Fundamentals course...')
        
        course, _ = Course.objects.get_or_create(
            slug='linux-fundamentals',
            defaults={
                'title': 'Linux Fundamentals',
                'description': 'Master the Linux command line and essential system administration skills. Perfect for beginners!',
                'level': 'beginner',
                'status': 'published'
            }
        )
        
        # Module 1: Getting Started
        module1, _ = Module.objects.get_or_create(
            course=course,
            title='Getting Started with Linux',
            defaults={'order': 1, 'description': 'Introduction to Linux and the command line'}
        )
        
        lesson1, _ = Lesson.objects.get_or_create(
            module=module1,
            title='Welcome to the Terminal',
            defaults={
                'order': 1,
                'content': '''# Welcome to the Terminal!

The terminal (also called command line or shell) is your gateway to mastering Linux and cybersecurity.

## Why Learn the Terminal?

- **Power**: Execute commands faster than GUI
- **Automation**: Script repetitive tasks
- **Remote Access**: Control servers from anywhere
- **Hacking Tools**: Most security tools are command-line based

## Your First Commands

Let's start with the basics:

### `pwd` - Print Working Directory
Shows you where you are in the filesystem.

### `ls` - List Files
Displays files and folders in current directory.

### `cd` - Change Directory
Move to a different folder.

Now, let's try it in the lab!''',
                'content_type': 'text',
                'xp_reward': 50,
                'estimated_duration': 10
            }
        )
        
        # Create simulated environment
        env, _ = SimulatedEnvironment.objects.get_or_create(
            name='Linux Basics Environment',
            defaults={
                'description': 'Basic Linux file system for beginners',
                'filesystem': {
                    '/home/student/': {
                        'welcome.txt': 'Congratulations! You ran your first cat command.',
                        'secret.txt': 'FLAG{first_steps_complete}',
                        'documents/': {
                            'readme.md': 'This is a markdown file'
                        }
                    }
                },
                'simulated_user': 'student',
                'simulated_hostname': 'linux-lab'
            }
        )
        
        # LAB 1: Welcome to the Terminal
        Lab.objects.get_or_create(
            lesson=lesson1,
            title='Your First Commands',
            defaults={
                'description': 'Learn basic navigation commands in a real Linux terminal.',
                'instructions': '''## Objectives

1. Find out your current directory
2. List all files in the directory
3. Read the contents of welcome.txt
4. Find the hidden flag in secret.txt

## Commands You'll Need

- `pwd` - Show current directory
- `ls` - List files
- `cat <filename>` - Read file contents

**Tip**: Type `ls` first to see what files are available!''',
                'difficulty': 'easy',
                'xp_reward': 100,
                'time_limit': 15,
                'environment': env,
                'objectives': [
                    {'id': 1, 'description': 'Run pwd command', 'command': 'pwd'},
                    {'id': 2, 'description': 'List files with ls', 'command': 'ls'},
                    {'id': 3, 'description': 'Read welcome.txt', 'command': 'cat welcome.txt'},
                    {'id': 4, 'description': 'Find the flag', 'command': 'cat secret.txt'}
                ],
                'hints': [
                    'Start by typing `ls` to see available files',
                    'Use `cat filename` to read a file',
                    'The flag is in secret.txt'
                ],
                'flags': ['FLAG{first_steps_complete}'],
                'solution_guide': '''### Solution

1. **Check current directory**:
   ```
   pwd
   ```
   Output: `/home/student`

2. **List files**:
   ```
   ls
   ```
   You should see: welcome.txt, secret.txt, documents/

3. **Read welcome.txt**:
   ```
   cat welcome.txt
   ```

4. **Get the flag**:
   ```
   cat secret.txt
   ```
   Flag: `FLAG{first_steps_complete}`

Congratulations! You've completed your first lab!''',
                'xp_penalty_for_solution': 30
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Linux Fundamentals created'))

    def create_web_security(self):
        self.stdout.write('Creating Web Security Basics course...')
        
        course, _ = Course.objects.get_or_create(
            slug='web-security',
            defaults={
                'title': 'Web Security Basics',
                'description': 'Learn the OWASP Top 10 vulnerabilities and how to find them. Hands-on practice with real exploits in a safe environment.',
                'level': 'intermediate',
                'status': 'published'
            }
        )
        
        # Module 1: Introduction
        module1, _ = Module.objects.get_or_create(
            course=course,
            title='OWASP Top 10 Introduction',
            defaults={'order': 1, 'description': 'Understanding the most critical web security risks'}
        )
        
        lesson1, _ = Lesson.objects.get_or_create(
            module=module1,
            title='What is OWASP Top 10?',
           defaults={
                'order': 1,
                'content': '''# OWASP Top 10

The OWASP Top 10 is a standard awareness document for developers and web application security. It represents a broad consensus about the most critical security risks to web applications.

## The Top 10 (2021)

1. **Broken Access Control**
2. **Cryptographic Failures**
3. **Injection** ← We'll practice this!
4. **Insecure Design**
5. **Security Misconfiguration**
6. **Vulnerable and Outdated Components**
7. **Identification and Authentication Failures**
8. **Software and Data Integrity Failures**
9. **Security Logging and Monitoring Failures**
10. **Server-Side Request Forgery (SSRF)**

## Why This Matters

- 🎯 **Job Skills**: Most security jobs require OWASP knowledge
- 🛡️ **Defense**: Learn how attacks work to defend against them
- 🔒 **Compliance**: Many regulations require OWASP compliance

Let's dive into Injection attacks!''',
                'content_type': 'text',
                'xp_reward': 75,
                'estimated_duration': 15
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Web Security Basics created'))

    def create_achievements(self):
        self.stdout.write('Creating achievements...')
        
        Achievement.objects.get_or_create(
            slug='first-steps',
            defaults={
                'name': 'First Steps',
                'description': 'Complete your first lesson',
                'category': 'progress',
                'requirements': {'type': 'lessons_completed', 'count': 1},
                'xp_reward': 25
            }
        )
        
        Achievement.objects.get_or_create(
            slug='lab-beginner',
            defaults={
                'name': 'Lab Beginner',
                'description': 'Complete 5 labs',
                'category': 'skill',
                'requirements': {'type': 'labs_completed', 'count': 5},
                'xp_reward': 100
            }
        )
        
        Achievement.objects.get_or_create(
            slug='xp-milestone',
            defaults={
                'name': 'XP Milestone',
                'description': 'Earn 500 total XP',
                'category': 'progress',
                'requirements': {'type': 'total_xp', 'amount': 500},
                'xp_reward': 150
            }
        )
        
        Achievement.objects.get_or_create(
            slug='week-warrior',
            defaults={
                'name': 'Week Warrior',
                'description': 'Maintain a 7-day learning streak',
                'category': 'challenge',
                'requirements': {'type': 'streak_days', 'days': 7},
                'xp_reward': 200
            }
        )
        
        Achievement.objects.get_or_create(
            slug='course-conqueror',
            defaults={
                'name': 'Course Conqueror',
                'description': 'Complete your first full course',
                'category': 'progress',
                'requirements': {'type': 'courses_completed', 'count': 1},
                'xp_reward': 300
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Achievements created'))
