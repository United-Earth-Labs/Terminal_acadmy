# PostgreSQL Production Setup - Quick Start

## 🚀 For Team Members: 5-Minute Setup

### What You Need
1. **PostgreSQL installed** on your machine
2. **Project dependencies** installed: `pip install -r requirements/base.txt`

### Quick Setup Steps

#### 1. Install PostgreSQL
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Mac**: `brew install postgresql@16`
- **Linux**: `sudo apt install postgresql postgresql-contrib`

#### 2. Create Database (Choose One Method)

**Method A: Use Our Script (Recommended)**
```bash
python scripts/setup_postgres.py
```
Follow the prompts and it will create everything for you.

**Method B: Manual Setup**
```bash
# Open PostgreSQL terminal
psql -U postgres

# Run these commands:
CREATE USER terminal_user WITH PASSWORD 'your_password';
CREATE DATABASE terminal_academy OWNER terminal_user;
GRANT ALL PRIVILEGES ON DATABASE terminal_academy TO terminal_user;
\q
```

#### 3. Configure Environment

Create a `.env` file in the project root:

```env
# For local testing with PostgreSQL
DATABASE_URL=postgresql://terminal_user:your_password@localhost:5432/terminal_academy
DJANGO_SETTINGS_MODULE=core.settings.production
DEBUG=True
SECRET_KEY=your-local-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Or keep using SQLite for development:**
```env
DJANGO_SETTINGS_MODULE=core.settings.development
DEBUG=True
SECRET_KEY=your-local-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 4. Run Migrations

```bash
# Windows PowerShell
$env:DJANGO_SETTINGS_MODULE="core.settings.production"

# Linux/Mac
export DJANGO_SETTINGS_MODULE=core.settings.production

# Run migrations
python manage.py migrate
python manage.py createcachetable
python manage.py createsuperuser
```

#### 5. Test It

```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## 🌐 For Production Deployment

### Environment Variables Needed

```env
# Required
DEBUG=False
SECRET_KEY=<generate-with-django-command>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Recommended
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Deployment Checklist

- [ ] PostgreSQL database created
- [ ] `DATABASE_URL` configured
- [ ] `SECRET_KEY` generated and set (use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` configured
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py createcachetable`
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Run `python manage.py createsuperuser`
- [ ] Configure web server (Gunicorn + Nginx)
- [ ] Setup SSL certificate
- [ ] Configure backups

---

## 📚 Full Documentation

For detailed instructions, troubleshooting, and advanced configuration:

👉 **[See POSTGRESQL_SETUP_GUIDE.md](./POSTGRESQL_SETUP_GUIDE.md)**

---

## 🆘 Quick Troubleshooting

**Connection refused?**
```bash
# Check PostgreSQL is running
pg_isready

# Windows: Start service from Services app
# Linux: sudo service postgresql start
```

**Authentication failed?**
```bash
# Check your .env file has correct DATABASE_URL
# Make sure password doesn't have special characters (or URL-encode them)
```

**Tables not found?**
```bash
# Run migrations
python manage.py migrate
```

**Still stuck?** Read the full guide: [POSTGRESQL_SETUP_GUIDE.md](./POSTGRESQL_SETUP_GUIDE.md)

---

## 🔄 Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| **Database** | SQLite (`db.sqlite3`) | PostgreSQL |
| **Settings** | `core.settings.development` | `core.settings.production` |
| **DEBUG** | `True` | `False` |
| **Server** | `runserver` | Gunicorn + Nginx |
| **Static Files** | Dev server | WhiteNoise + CDN |
| **Email** | Console | SMTP |
| **SSL** | No | Required |
| **Backups** | Optional | **Required** |

---

**Quick Links:**
- 📖 [Full Setup Guide](./POSTGRESQL_SETUP_GUIDE.md)
- 🐘 [PostgreSQL Docs](https://www.postgresql.org/docs/)
- 🎯 [Django Database Docs](https://docs.djangoproject.com/en/5.0/ref/databases/)
