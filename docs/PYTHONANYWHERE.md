# PythonAnywhere Deployment Guide 🐍

Step-by-step guide to deploy Terminal Academy on PythonAnywhere.

---

## 1. Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Sign up for a **free** or **paid** account
3. Free tier works for testing (limited CPU, bandwidth)

---

## 2. Upload Your Code

### Option A: Git (Recommended)
```bash
# In PythonAnywhere Bash console:
cd ~
git clone https://github.com/YOUR_USERNAME/terminal_academy.git
```

### Option B: Upload ZIP
1. Zip your project folder
2. Upload via Files tab
3. Unzip in Bash console: `unzip terminal_academy.zip`

---

## 3. Create Virtual Environment

```bash
cd ~/terminal_academy
mkvirtualenv terminal_academy --python=/usr/bin/python3.11
pip install -r requirements/production.txt
```

---

## 4. Configure Database

### SQLite (Free tier):
Already configured! No changes needed.

### PostgreSQL (Paid only):
1. Go to Databases tab
2. Create PostgreSQL database
3. Update `.env`:
```
DATABASE_URL=postgres://user:password@host:port/dbname
```

---

## 5. Create Environment File

```bash
cd ~/terminal_academy
cp .env.example .env
nano .env
```

Update these values:
```env
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key
ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com
```

---

## 6. Initialize Database

```bash
python manage.py migrate
python manage.py createcachetable  # Required for database cache
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## 7. Configure Web App

1. Go to **Web** tab → **Add a new web app**
2. Choose **Manual configuration** → **Python 3.11**
3. Set these values:

### Source code:
```
/home/YOUR_USERNAME/terminal_academy
```

### Virtualenv:
```
/home/YOUR_USERNAME/.virtualenvs/terminal_academy
```

### WSGI file:
Click the link and replace contents with:

```python
import os
import sys

# Add your project to path
path = '/home/YOUR_USERNAME/terminal_academy'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Static files:
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/terminal_academy/staticfiles` |
| `/media/` | `/home/YOUR_USERNAME/terminal_academy/media` |

---

## 8. Set Up Scheduled Tasks

Go to **Tasks** tab and add:

### Daily cleanup (runs at 4:00 AM):
```
cd ~/terminal_academy && /home/YOUR_USERNAME/.virtualenvs/terminal_academy/bin/python manage.py cleanup
```

---

## 9. Reload Web App

Click **Reload** button on the Web tab.

Visit: `https://YOUR_USERNAME.pythonanywhere.com`

---

## 🎉 You're Live!

### Admin Panel:
`https://YOUR_USERNAME.pythonanywhere.com/admin/`

### Test Health:
`https://YOUR_USERNAME.pythonanywhere.com/health/`

---

## Troubleshooting

### Error logs:
Check the **error log** link on Web tab.

### Common issues:
- **500 error**: Check ALLOWED_HOSTS includes your domain
- **Static files missing**: Run `collectstatic` again
- **Database error**: Run `migrate` and `createcachetable`

---

## Upgrading Code

```bash
cd ~/terminal_academy
git pull origin main
pip install -r requirements/production.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Then click "Reload" on Web tab
```
