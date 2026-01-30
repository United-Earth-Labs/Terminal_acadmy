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
        
        # MODULE 1: Web Security Basics - LESSON 1
        module1, _ = Module.objects.get_or_create(
            course=course,
            title='Web Security Basics',
            defaults={'order': 1, 'description': 'Understanding web application security fundamentals'}
        )
        
        # LESSON 1: Web Application Architecture & Attack Surfaces
        lesson1, _ = Lesson.objects.get_or_create(
            module=module1,
            title='Web Application Architecture & Attack Surfaces',
            defaults={
                'order': 1,
                'content': '''🛡️ **Lesson 1: Web Application Architecture & Attack Surfaces**

**Module:** Web Security Basics (Intermediate)  
**Lesson:** 1 / 15  
**Difficulty:** Intermediate  
**Estimated Time:** 25–30 minutes

---

## 🎯 Learning Objectives

By the end of this lesson, you will:

✅ Understand how a web application is structured  
✅ Identify where security vulnerabilities usually appear  
✅ Learn the concept of **attack surfaces**  
✅ Start thinking like a security-aware developer

---

## 🌐 What Is a Web Application?

A web application is **not a single program**.  
It is a **system of multiple components** working together.

### Typical Components:

1. **Client (Browser)**
2. **Web Server**
3. **Application Logic**
4. **Database**
5. **External Services (APIs)**

**⚠️ Each component introduces security risks.**

---

## 🧱 Basic Web Architecture Flow

```
User (Browser)
   ↓
Web Server (Nginx / Django)
   ↓
Application Logic
   ↓
Database
   ↑
Response back to User
```

**⚠️ Security issues appear at every arrow.**

---

## 🔓 Trust Boundaries (Very Important Concept)

A **trust boundary** is a point where:

> Data moves from an **untrusted source** to a **trusted system**.

### Examples:

- User input → backend
- API response → database
- Cookie → authentication system

### ❗ Golden Rule:

**Never trust user-controlled data.**

---

## 🎯 What Is an Attack Surface?

An **attack surface** is:

> Any place where an attacker can send input to your application.

### Common Attack Surfaces:

- Login forms
- Search fields
- File uploads
- URL parameters
- API endpoints
- Cookies
- HTTP headers

**⚠️ The larger the attack surface → the higher the risk.**

---

## 🧪 Example: Simple Login Page

```http
POST /login
email=user@example.com
password=*******
```

### Potential Risks:

❌ Weak password handling  
❌ No rate limiting  
❌ Poor input validation  
❌ Missing HTTPS

**Even a simple form can be dangerous.**

---

## 🧠 Developer vs Security Mindset

### Normal Developer Thinks:

✅ "Does this feature work?"

### Security-Aware Developer Thinks:

🔐 "What if this feature is **abused**?"

**Security is not about breaking systems,  
it's about preventing misuse.**

---

## 💡 Concrete Code Example

### ⚠️ Vulnerable Code:

```python
# Dangerous: No validation!
def login(request):
    email = request.POST['email']  # ⚠️ No validation!
    password = request.POST['password']
    
    # 🔓 SQL Injection risk!
    query = f"SELECT * FROM users WHERE email='{email}'"
    user = db.execute(query)
    
    if user and user.password == password:
        return "Login successful"
    return "Login failed"
```

### ✅ Secure Code:

```python
# Better: Using parameterized queries
def login(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    
    # ✅ Parameterized query prevents SQL injection
    query = "SELECT * FROM users WHERE email = ?"
    user = db.execute(query, [email])
    
    # ✅ Use proper password hashing
    if user and check_password_hash(user.password_hash, password):
        return create_session(user)
    return "Login failed"
```

---

## 🔐 Real-World Security Insight

Many major breaches happened because:

❌ Developers **trusted input**  
❌ Assumed users **behave correctly**  
❌ Missed **access checks**

**Most vulnerabilities are logic flaws, not advanced hacks.**

---

## 🗺️ Attack Surface Map

```
┌─────────────────────┐
│   User Browser      │ ← User-Controlled (UNTRUSTED)
└──────────┬──────────┘
           │ HTTP Request (Attack Vector)
           ▼
┌─────────────────────┐
│   Web Server        │ ← Trust Boundary #1
└──────────┬──────────┘
           │ SQL Queries
           ▼
┌─────────────────────┐
│  Database           │ ← Trust Boundary #2
└─────────────────────┘
```

---

## 🧪 Interactive Terminal Lab

You will practice identifying attack surfaces in a simulated web application.

**Lab Name:** Identify Attack Surfaces  
**Environment:** Simulated Web Server  
**Tools:** `curl`, `analyze-app`, `inspect-headers`

### Your Tasks:

1. Analyze the web application endpoints
2. Identify user-controlled inputs
3. Determine which inputs need validation
4. Extract the security flag

**Proceed to the lab to continue!**

---

## ❓ Knowledge Check

Before completing this lesson, answer these questions:

### Question 1:
**What is a trust boundary?**

✅ **Correct Answer:** A point where data moves from an untrusted source to a trusted system.

---

### Question 2:
**Name three common attack surfaces.**

✅ **Correct Answer:** Login forms, file uploads, URL parameters, search fields, cookies, or API endpoints.

---

### Question 3:
**Why should user input never be trusted?**

✅ **Correct Answer:** Because users (including attackers) have full control over their input and can send malicious data to exploit vulnerabilities.

---

## 🔐 Ethical Reminder

All labs in Terminal Academy are:

✅ **Simulated**  
✅ **Controlled**  
✅ **Legal**

**No real systems are targeted.**

---

## ✅ Lesson Completion Criteria

To complete this lesson, you must:

✔ Read the full lesson  
✔ Complete the terminal lab  
✔ Answer the knowledge check (3/3 correct)

---

## ➡️ Next Lesson Preview

### **Lesson 2: HTTP Request Lifecycle & Security**

You will learn:

- How requests are processed
- Where attackers inject data
- Why request structure matters

**See you in the next lesson!** 🚀''',
                'content_type': 'text',
                'xp_reward': 150,
                'estimated_duration': 30
            }
        )
        
        # Create environment for Lesson 1 lab
        env1, _ = SimulatedEnvironment.objects.get_or_create(
            name='Web Attack Surface Analysis Environment',
            defaults={
                'description': 'Simulated web application for analyzing attack surfaces',
                'filesystem': {
                    '/var/www/app/': {
                        'routes.py': '''# Web Application Routes
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']  # User input
    password = request.form['password']  # User input
    return authenticate(email, password)

@app.route('/search')
def search():
    query = request.args.get('q')  # URL parameter
    return search_database(query)

@app.route('/profile')
def profile():
    user_id = request.args.get('id')  # URL parameter
    return get_user_profile(user_id)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['document']  # File upload
    return save_file(file)
''',
                        'config.json': '''{
    "api_endpoints": [
        "/api/users",
        "/api/posts",
        "/api/comments"
    ],
    "security_flag": "FLAG{attack_surface_identified}"
}''',
                        'README.txt': '''This is a simulated web application.
Your task is to identify all attack surfaces.

Commands available:
- analyze-app: List all endpoints
- curl -X POST /endpoint: Test endpoints
- inspect-headers /endpoint: View HTTP headers
- cat filename: Read files
'''
                    }
                },
                'simulated_user': 'security-student',
                'simulated_hostname': 'webapp-lab'
            }
        )
        
        # LAB 1: Attack Surface Analysis
        Lab.objects.get_or_create(
            lesson=lesson1,
            title='Identify Web Application Attack Surfaces',
            defaults={
                'description': 'Practice identifying attack surfaces in a web application by analyzing endpoints, inputs, and potential vulnerability points.',
                'instructions': '''## 🎯 Mission

You've been given access to a web application's source code and configuration.  
Your job is to **identify all attack surfaces** and determine which inputs need security validation.

---

## 📋 Objectives

1. List all available application endpoints
2. Identify user-controlled inputs (forms, URL parameters, headers)
3. Analyze which endpoints accept user data
4. Find the security flag in the configuration

---

## 🛠️ Commands You'll Need

### Analysis Commands:
```bash
analyze-app              # List all endpoints and their methods
curl -X POST /login      # Test login endpoint
inspect-headers /search  # View HTTP headers for endpoint
cat routes.py            # View application routes
cat config.json          # View configuration
ls -la                   # List all files
```

### Example Usage:
```bash
student@webapp-lab:~$ analyze-app
Detected Input Points:
- /login (POST) - Accepts: email, password
- /search (GET) - Accepts: q parameter
...
```

---

## 💡 What to Look For

### Attack Surfaces Include:
- **Forms**: Login, registration, contact forms
- **URL Parameters**: ?id=123, ?search=query
- **File Uploads**: Document uploads, image uploads
- **Headers**: Cookies, User-Agent, custom headers
- **API Endpoints**: REST APIs, JSON data

### Security Questions to Ask:
1. Is user input validated?
2. Are there SQL queries using user data?
3. Can files be uploaded without restrictions?
4. Are there rate limits on sensitive endpoints?

---

## 🎯 Your Tasks

✅ **Task 1:** Run `analyze-app` to see all endpoints  
✅ **Task 2:** Use `cat routes.py` to view the code  
✅ **Task 3:** Identify at least 4 attack surfaces  
✅ **Task 4:** Find the flag in `config.json`

---

## 🚨 Hint

The flag is hidden in the configuration file. Use `cat` to read it!

**Good luck, security analyst!** 🔐''',
                'difficulty': 'easy',
                'xp_reward': 200,
                'time_limit': 30,
                'environment': env1,
                'objectives': [
                    {'id': 1, 'description': 'List all files in the application', 'command': 'ls -la'},
                    {'id': 2, 'description': 'View application routes', 'command': 'cat routes.py'},
                    {'id': 3, 'description': 'Analyze attack surfaces', 'command': 'analyze-app'},
                    {'id': 4, 'description': 'Find the security flag', 'command': 'cat config.json'}
                ],
                'hints': [
                    'Start with ls -la to see all available files',
                    'The routes.py file contains all the endpoints',
                    'Use analyze-app to get a summary of attack surfaces',
                    'The flag is in config.json - use cat to read it'
                ],
                'flags': ['FLAG{attack_surface_identified}'],
                'solution_guide': '''## 🎓 Solution Guide

### Step 1: List Files
```bash
ls -la
```

**Output:**
```
total 3
-rw-r--r-- 1 student student  234 Jan 20 routes.py
-rw-r--r-- 1 student student  156 Jan 20 config.json
-rw-r--r-- 1 student student  312 Jan 20 README.txt
```

---

### Step 2: Analyze Routes
```bash
cat routes.py
```

**Identified Attack Surfaces:**
1. `/login` - POST - email, password inputs
2. `/search` - GET - query parameter
3. `/profile` - GET - user_id parameter
4. `/upload` - POST - file upload

---

### Step 3: Run Analysis Tool
```bash
analyze-app
```

**Output:**
```
Detected Input Points:
- /login (POST) - email, password
- /search?q= (GET) - query parameter
- /profile?id= (GET) - user_id parameter
- /upload (POST) - file upload
- Cookie: session_id
- Header: User-Agent
```

**Total Attack Surfaces: 6**

---

### Step 4: Get the Flag
```bash
cat config.json
```

**Flag Found:** `FLAG{attack_surface_identified}`

---

## 🎯 Key Takeaways

✅ Every user input is a potential attack surface  
✅ Always analyze endpoints for security risks  
✅ URL parameters are often overlooked attack vectors  
✅ File uploads require special validation  

**Congratulations! You've completed the lab!** 🎉''',
                'xp_penalty_for_solution': 50
            }
        )
        
        # Module 2: Injection Attacks
        module2, _ = Module.objects.get_or_create(
            course=course,
            title='Injection Attacks',
            defaults={'order': 2, 'description': 'SQL Injection and Command Injection'}
        )
        
        lesson2, _ = Lesson.objects.get_or_create(
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
        
        self.stdout.write(self.style.SUCCESS('  ✓ Web Security expanded with enhanced Lesson 1'))

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
