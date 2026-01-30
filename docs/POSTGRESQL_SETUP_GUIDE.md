# PostgreSQL Setup Guide - Terminal Academy

## 📋 Overview

This guide walks you through setting up PostgreSQL for **production** deployment while maintaining SQLite for **local development**. Our Django project is already configured to support both databases seamlessly.

> [!IMPORTANT]
> **Development = SQLite** (Simple, file-based, no setup needed)  
> **Production = PostgreSQL** (Robust, scalable, production-ready)

---

## 🎯 Quick Summary

- ✅ **Already Configured**: Django settings split (development/production)
- ✅ **Already Installed**: `psycopg2-binary` and `dj-database-url` in requirements
- 🔧 **What You Need**: Install PostgreSQL, create database, set environment variables
- 🚀 **What You'll Do**: Follow steps below for local PostgreSQL testing OR production deployment

---

## 📦 Part 1: Installing PostgreSQL

### Option A: Windows Installation

1. **Download PostgreSQL**
   - Visit: https://www.postgresql.org/download/windows/
   - Download the latest stable version (PostgreSQL 16.x recommended)
   - Use the interactive installer by EDB

2. **Run the Installer**
   - Click through the installer
   - **Remember the password** you set for the `postgres` superuser!
   - Default port: `5432` (keep as default)
   - Keep default locale settings

3. **Verify Installation**
   ```powershell
   # Check PostgreSQL is running
   psql --version
   
   # Should output: psql (PostgreSQL) 16.x
   ```

4. **Add to PATH** (if not done automatically)
   - Search "Environment Variables" in Windows
   - Edit System Environment Variables
   - Add `C:\Program Files\PostgreSQL\16\bin` to PATH
   - Restart your terminal

### Option B: Linux/WSL Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo service postgresql start

# Check status
sudo service postgresql status
```

### Option C: macOS Installation

```bash
# Using Homebrew
brew install postgresql@16

# Start PostgreSQL
brew services start postgresql@16

# Verify
psql --version
```

### Option D: Docker (Cross-Platform)

```bash
# Pull PostgreSQL image
docker pull postgres:16-alpine

# Run PostgreSQL container
docker run --name terminal-academy-db \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_USER=terminal_user \
  -e POSTGRES_DB=terminal_academy \
  -p 5432:5432 \
  -d postgres:16-alpine

# Verify it's running
docker ps
```

---

## 🗄️ Part 2: Creating the Database

### Method 1: Using psql Command Line

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Inside psql, run these commands:
```

```sql
-- Create a dedicated user for Terminal Academy
CREATE USER terminal_user WITH PASSWORD 'your_secure_password_here';

-- Create the database
CREATE DATABASE terminal_academy OWNER terminal_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE terminal_academy TO terminal_user;

-- Exit psql
\q
```

### Method 2: Using pgAdmin (GUI)

1. **Open pgAdmin** (installed with PostgreSQL)
2. **Connect to PostgreSQL Server**
   - Right-click "Servers" → Register → Server
   - Name: `Terminal Academy Local`
   - Host: `localhost`
   - Port: `5432`
   - Username: `postgres`
   - Password: (the one you set during installation)

3. **Create User**
   - Right-click "Login/Group Roles" → Create → Login/Group Role
   - Name: `terminal_user`
   - Password: `your_secure_password_here`
   - Privileges: Check "Can login"

4. **Create Database**
   - Right-click "Databases" → Create → Database
   - Database: `terminal_academy`
   - Owner: `terminal_user`

### Method 3: Using SQL Script

Save this as `setup_database.sql`:

```sql
-- Create user
CREATE USER terminal_user WITH PASSWORD 'change_me_in_production';

-- Create database
CREATE DATABASE terminal_academy 
    OWNER terminal_user
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE terminal_academy TO terminal_user;

-- Connect to the database
\c terminal_academy

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO terminal_user;
```

Run it:
```bash
psql -U postgres -f setup_database.sql
```

---

## ⚙️ Part 3: Configuring Django

### Step 1: Environment Variables Setup

Our project already supports environment-based configuration. You need to create/update your `.env` file.

#### For Local Development with PostgreSQL

Create `.env` in project root:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-local-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
DATABASE_URL=postgresql://terminal_user:your_secure_password_here@localhost:5432/terminal_academy

# Email (console for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

#### For Production Deployment

Create `.env` or `.env.production`:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=generate-a-very-long-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# PostgreSQL Database Production
DATABASE_URL=postgresql://terminal_user:PRODUCTION_PASSWORD@db-host:5432/terminal_academy
# Or with connection parameters:
# DATABASE_URL=postgresql://user:pass@hostname:5432/dbname?sslmode=require

# Email (use real SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Security
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

> [!TIP]
> **Generate a Secure Secret Key:**
> ```python
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### Step 2: Database URL Format

The `DATABASE_URL` follows this pattern:

```
postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE_NAME]
```

**Examples:**

```bash
# Local development
DATABASE_URL=postgresql://terminal_user:mypassword@localhost:5432/terminal_academy

# Production with SSL
DATABASE_URL=postgresql://prod_user:secure_pass@db.example.com:5432/terminal_prod?sslmode=require

# Docker container (from another container)
DATABASE_URL=postgresql://terminal_user:password@db:5432/terminal_academy

# Cloud services (example RDS)
DATABASE_URL=postgresql://admin:pass@terminal-db.xxxxx.us-east-1.rds.amazonaws.com:5432/terminal_academy
```

### Step 3: Understanding the Settings Files

Our Django project uses a **split settings approach**:

```
core/settings/
├── __init__.py
├── base.py          # Shared settings for all environments
├── development.py   # Development-specific (uses SQLite by default)
└── production.py    # Production-specific (uses DATABASE_URL)
```

**How it works:**

- **`base.py`**: Uses `dj-database-url` to read `DATABASE_URL` from environment
  ```python
  DATABASES = {
      'default': dj_database_url.config(
          default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),  # Fallback
          conn_max_age=600,
          conn_health_checks=True,
      )
  }
  ```

- **`development.py`**: Overrides to force SQLite
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
      }
  }
  ```

- **`production.py`**: Uses DATABASE_URL from environment (inherits from base.py)

---

## 🚀 Part 4: Running Migrations

### Step 1: Set Django Settings Module

Choose your environment:

**For Development (SQLite):**
```bash
# Windows PowerShell
$env:DJANGO_SETTINGS_MODULE="core.settings.development"

# Windows CMD
set DJANGO_SETTINGS_MODULE=core.settings.development

# Linux/Mac
export DJANGO_SETTINGS_MODULE=core.settings.development
```

**For Production (PostgreSQL):**
```bash
# Windows PowerShell
$env:DJANGO_SETTINGS_MODULE="core.settings.production"

# Windows CMD
set DJANGO_SETTINGS_MODULE=core.settings.production

# Linux/Mac
export DJANGO_SETTINGS_MODULE=core.settings.production
```

> [!NOTE]
> You can also set this in your `.env` file:
> ```bash
> DJANGO_SETTINGS_MODULE=core.settings.production
> ```

### Step 2: Verify Database Connection

```bash
# Test database connection
python manage.py check --database default

# Should output: System check identified no issues (0 silenced).
```

### Step 3: Create Cache Table

Our app uses database caching:

```bash
python manage.py createcachetable
```

### Step 4: Run Migrations

```bash
# Show what migrations will run
python manage.py showmigrations

# Run all migrations
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying users.0001_initial... OK
#   Applying courses.0001_initial... OK
#   ... (many more)
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser

# Follow prompts:
# Email: admin@terminalacademy.com
# Username: admin
# Password: (choose a strong password)
```

### Step 6: Collect Static Files (Production Only)

```bash
python manage.py collectstatic --noinput
```

---

## ✅ Part 5: Testing the Setup

### Test 1: Check Database Connection

```bash
python manage.py dbshell
```

This should open a PostgreSQL prompt:
```
terminal_academy=> \dt
# Should list all your Django tables
```

Exit with `\q`

### Test 2: Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

- ✅ Homepage loads
- ✅ Admin panel works: http://localhost:8000/admin/
- ✅ Can log in with superuser

### Test 3: Verify Data Persistence

```bash
# Create some test data
python manage.py shell
```

```python
from users.models import CustomUser
from courses.models import Course

# Check users
print(f"Total users: {CustomUser.objects.count()}")

# Check courses
print(f"Total courses: {Course.objects.count()}")

# Exit
exit()
```

### Test 4: Check PostgreSQL Directly

```bash
# Connect to database
psql -U terminal_user -d terminal_academy

# Inside psql:
\dt                          # List all tables
SELECT * FROM users_customuser LIMIT 5;  # Check users table
\q                           # Exit
```

---

## 🔧 Part 6: Common Issues & Troubleshooting

### Issue 1: "FATAL: role does not exist"

**Problem:** PostgreSQL user not created

**Solution:**
```sql
-- Connect as superuser
psql -U postgres

-- Create the user
CREATE USER terminal_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE terminal_academy TO terminal_user;
```

### Issue 2: "peer authentication failed"

**Problem:** PostgreSQL authentication method issue

**Solution:** Edit `pg_hba.conf`:

```bash
# Find the file location
psql -U postgres -c "SHOW hba_file;"

# Edit the file (Windows: notepad, Linux: nano/vim)
# Change from:
local   all   all   peer

# To:
local   all   all   md5
```

Then restart PostgreSQL:
```bash
# Windows
services.msc  # Find PostgreSQL service and restart

# Linux
sudo service postgresql restart

# Docker
docker restart terminal-academy-db
```

### Issue 3: "connection refused on port 5432"

**Problem:** PostgreSQL not running

**Solution:**
```bash
# Windows: Open Services, start PostgreSQL
# Linux:
sudo service postgresql start

# Docker:
docker start terminal-academy-db
```

### Issue 4: "django.db.utils.OperationalError: FATAL: database does not exist"

**Problem:** Database not created

**Solution:**
```sql
CREATE DATABASE terminal_academy OWNER terminal_user;
```

### Issue 5: "psycopg2 not installed"

**Problem:** Missing PostgreSQL adapter

**Solution:**
```bash
pip install psycopg2-binary
# Or from requirements:
pip install -r requirements/base.txt
```

### Issue 6: Migrations not applying

**Solution:**
```bash
# Reset migrations (DANGER: loses data!)
python manage.py migrate --fake-initial

# Or force migrate:
python manage.py migrate --run-syncdb
```

### Issue 7: "relation does not exist" errors

**Problem:** Tables not created

**Solution:**
```bash
# Check migration status
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# If stuck, try:
python manage.py migrate --fake-initial
```

---

## 🌐 Part 7: Production Deployment Scenarios

### Scenario A: Deploy to PythonAnywhere

1. **Upload Code**
   ```bash
   git clone https://github.com/yourusername/terminal_academy.git
   ```

2. **Install Requirements**
   ```bash
   pip3.11 install --user -r requirements/base.txt
   ```

3. **Setup PostgreSQL on PythonAnywhere**
   - PythonAnywhere offers PostgreSQL for paid accounts
   - Get connection details from PythonAnywhere dashboard
   - DATABASE_URL format: `postgresql://username:password@username-xxxx.postgres.pythonanywhere-services.com:10xxx/username$terminal_academy`

4. **Configure Environment**
   - Set environment variables in WSGI file or use `.env`
   - Set `DJANGO_SETTINGS_MODULE=core.settings.production`

5. **Run Setup**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

### Scenario B: Deploy to Heroku

1. **Add Heroku PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

2. **Heroku automatically sets `DATABASE_URL`**
   ```bash
   heroku config
   # DATABASE_URL is already set
   ```

3. **Configure Other Environment Variables**
   ```bash
   heroku config:set DJANGO_SETTINGS_MODULE=core.settings.production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set ALLOWED_HOSTS=yourapp.herokuapp.com
   ```

4. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Scenario C: Deploy to DigitalOcean/AWS/VPS

1. **Install PostgreSQL on Server**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE USER terminal_user WITH PASSWORD 'strong_password';
   CREATE DATABASE terminal_academy OWNER terminal_user;
   GRANT ALL PRIVILEGES ON DATABASE terminal_academy TO terminal_user;
   ```

3. **Configure PostgreSQL for Remote Access** (if needed)
   
   Edit `/etc/postgresql/16/main/postgresql.conf`:
   ```
   listen_addresses = '*'
   ```
   
   Edit `/etc/postgresql/16/main/pg_hba.conf`:
   ```
   host    all    all    0.0.0.0/0    md5
   ```
   
   Restart:
   ```bash
   sudo systemctl restart postgresql
   ```

4. **Setup Django Application**
   ```bash
   # Create .env file
   DATABASE_URL=postgresql://terminal_user:password@localhost:5432/terminal_academy
   DJANGO_SETTINGS_MODULE=core.settings.production
   DEBUG=False
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=your-domain.com
   
   # Run setup
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

5. **Setup Gunicorn + Nginx**
   ```bash
   gunicorn core.wsgi:application --bind 0.0.0.0:8000
   ```

### Scenario D: Docker Deployment

We already have a `docker-compose.yml`. To use it:

1. **Review docker-compose.yml**
   ```yaml
   services:
     db:
       image: postgres:16-alpine
       environment:
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
         POSTGRES_USER: terminal_user
         POSTGRES_DB: terminal_academy
   ```

2. **Create .env.production**
   ```bash
   POSTGRES_PASSWORD=secure_production_password
   DATABASE_URL=postgresql://terminal_user:secure_production_password@db:5432/terminal_academy
   DJANGO_SETTINGS_MODULE=core.settings.production
   ```

3. **Run Stack**
   ```bash
   docker-compose up -d
   
   # Run migrations
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

---

## 📊 Part 8: Database Management

### Backup Database

**PostgreSQL (pg_dump):**
```bash
# Full backup
pg_dump -U terminal_user -d terminal_academy > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U terminal_user -d terminal_academy | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup to custom format (recommended)
pg_dump -U terminal_user -d terminal_academy -F c -f backup_$(date +%Y%m%d).dump
```

**Using Django:**
```bash
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Specific apps only
python manage.py dumpdata users courses labs > backup_data.json
```

### Restore Database

**From SQL file:**
```bash
psql -U terminal_user -d terminal_academy < backup_20260129.sql
```

**From custom format:**
```bash
pg_restore -U terminal_user -d terminal_academy backup_20260129.dump
```

**Django loaddata:**
```bash
python manage.py loaddata backup_20260129.json
```

### Migrate from SQLite to PostgreSQL

```bash
# 1. Export data from SQLite
DJANGO_SETTINGS_MODULE=core.settings.development python manage.py dumpdata \
  --exclude auth.permission \
  --exclude contenttypes \
  --natural-foreign \
  --natural-primary \
  > data_dump.json

# 2. Switch to PostgreSQL
$env:DJANGO_SETTINGS_MODULE="core.settings.production"
# Set DATABASE_URL in .env

# 3. Run migrations on empty PostgreSQL
python manage.py migrate

# 4. Load data
python manage.py loaddata data_dump.json
```

### Database Performance

**Create Indexes:**
```sql
-- Connect to database
psql -U terminal_user -d terminal_academy

-- Check existing indexes
\di

-- Create custom indexes (example)
CREATE INDEX idx_users_email ON users_customuser(email);
CREATE INDEX idx_courses_created ON courses_course(created_at);
```

**Analyze Performance:**
```bash
python manage.py shell
```
```python
from django.db import connection
from django.db import reset_queries

# Enable query logging
from django.conf import settings
settings.DEBUG = True

# Run some queries
from courses.models import Course
courses = Course.objects.select_related('created_by').all()

# Check queries
print(connection.queries)
```

---

## 🔐 Part 9: Security Best Practices

### 1. Strong Passwords
- Use at least 20 characters for database passwords
- Use a password manager or generator
- Never commit passwords to git

### 2. Environment Variables
```bash
# ✅ Good - .env file (git-ignored)
DATABASE_URL=postgresql://user:pass@localhost/db

# ❌ Bad - hardcoded in settings.py
DATABASES = {'default': {'PASSWORD': 'mypassword'}}
```

### 3. Restrict Database Access
```sql
-- Only grant necessary permissions
GRANT CONNECT ON DATABASE terminal_academy TO terminal_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO terminal_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO terminal_user;
```

### 4. Use SSL for Remote Connections
```bash
DATABASE_URL=postgresql://user:pass@remote-host/db?sslmode=require
```

### 5. Regular Backups
```bash
# Automated daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U terminal_user terminal_academy | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

---

## 📝 Part 10: Quick Reference Commands

### PostgreSQL Commands

```bash
# Connect to database
psql -U terminal_user -d terminal_academy

# List databases
\l

# List tables
\dt

# Describe table
\d users_customuser

# Show table size
\dt+

# Exit psql
\q

# Run SQL file
psql -U terminal_user -d terminal_academy -f script.sql
```

### Django Commands

```bash
# Check database configuration
python manage.py check --database default

# Show migrations
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Database shell
python manage.py dbshell

# Python shell with Django
python manage.py shell

# Flush database (DANGER!)
python manage.py flush
```

---

## 🎓 Summary Checklist

### Initial Setup
- [ ] Install PostgreSQL
- [ ] Create database and user
- [ ] Install `psycopg2-binary` (already in requirements)
- [ ] Configure `.env` with `DATABASE_URL`
- [ ] Set `DJANGO_SETTINGS_MODULE` to production
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py createcachetable`
- [ ] Run `python manage.py createsuperuser`
- [ ] Test application

### Production Deployment
- [ ] Use strong `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variables (never hardcode secrets)
- [ ] Enable SSL for database connections
- [ ] Configure backups
- [ ] Run `python manage.py collectstatic`
- [ ] Setup monitoring and logging
- [ ] Test thoroughly

---

## 🆘 Getting Help

**Official Documentation:**
- Django Databases: https://docs.djangoproject.com/en/5.0/ref/databases/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- dj-database-url: https://github.com/jazzband/dj-database-url

**Common Issues:**
- Check PostgreSQL is running: `pg_isready`
- Check Django can connect: `python manage.py check --database default`
- View logs: `tail -f logs/django.log`
- PostgreSQL logs: `/var/log/postgresql/postgresql-16-main.log` (Linux)

**Contact:**
- Project repo: [Your GitHub URL]
- Team chat: [Your team communication channel]

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Maintainer:** Terminal Academy Dev Team

