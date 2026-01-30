"""
Populate enhanced Lesson 1 content for Web Security course.

Usage:
    python add_lesson1.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from courses.models import Course, Module, Lesson
from labs.models import Lab, SimulatedEnvironment

print('🚀 Adding enhanced Lesson 1: Web Application Architecture & Attack Surfaces...\n')

# Get or create Web Security course
course, created = Course.objects.get_or_create(
    slug='web-security',
    defaults={
        'title': 'Web Security Basics',
        'description': 'Learn the OWASP Top 10 vulnerabilities and how to find them. Hands-on practice with real exploits in a safe environment.',
        'level': 'intermediate',
        'status': 'published'
    }
)

if created:
    print('✓ Created Web Security course')
else:
    print('✓ Found existing Web Security course')

# Delete old modules if they exist to avoid conflicts
Module.objects.filter(course=course, title='OWASP Top 10 Introduction').delete()

# MODULE 1: Web Security Basics  
module1, created = Module.objects.get_or_create(
    course=course,
    order=1,
    defaults={'title': 'Web Security Basics', 'description': 'Understanding web application security fundamentals'}
)

if created:
    print('✓ Created Module: Web Security Basics')
else:
    # Update the title if it already exists
    module1.title = 'Web Security Basics'
    module1.description = 'Understanding web application security fundamentals'
    module1.save()
    print('✓ Updated Module: Web Security Basics')

# LESSON 1: Web Application Architecture & Attack Surfaces
lesson1, created = Lesson.objects.update_or_create(
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

if created:
    print('✓ Created Lesson 1: Web Application Architecture & Attack Surfaces')
else:
    print('✓ Updated Lesson 1: Web Application Architecture & Attack Surfaces')

# Create environment for Lesson 1 lab
env1, created = SimulatedEnvironment.objects.get_or_create(
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

if created:
    print('✓ Created Simulated Environment: Web Attack Surface Analysis')
else:
    print('✓ Found existing Simulated Environment')

# LAB 1: Attack Surface Analysis
lab1, created = Lab.objects.update_or_create(
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

if created:
    print('✓ Created Lab: Identify Web Application Attack Surfaces')
else:
    print('✓ Updated Lab: Identify Web Application Attack Surfaces')

print('\n✅ Enhanced Lesson 1 successfully added to Terminal Academy!')
print(f'✅ Course: {course.title}')
print(f'✅ Module: {module1.title}')
print(f'✅ Lesson: {lesson1.title}')
print(f'✅ Lab: {lab1.title}')
print('\n📚 You can now view this content at:')
print(f'   http://localhost:8000/courses/{course.slug}/')
print('\n🎉 Ready to learn about Attack Surfaces!')
