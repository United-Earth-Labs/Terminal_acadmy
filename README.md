# Terminal Academy 🖥️

> **Learn Ethical Hacking Through Interactive Terminal Labs**

A production-ready platform for teaching ethical hacking and cybersecurity in a safe, simulated environment. All commands execute in a sandboxed simulator - no real systems are ever accessed.

## ⚡ Quick Start

### Development (SQLite - Default)
```bash
# Clone and setup
git clone <repo-url>
cd terminal_academy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements/base.txt

# Configure environment
cp .env.example .env

# Run migrations
python manage.py migrate
python manage.py createcachetable

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Production with PostgreSQL

**📘 See detailed setup guide**: [docs/POSTGRESQL_SETUP_GUIDE.md](docs/POSTGRESQL_SETUP_GUIDE.md)  
**🚀 Quick reference**: [docs/POSTGRESQL_QUICKSTART.md](docs/POSTGRESQL_QUICKSTART.md)

```bash
# 1. Install PostgreSQL (see docs/POSTGRESQL_SETUP_GUIDE.md)

# 2. Create database (automated script)
python scripts/setup_postgres.py

# 3. Configure .env
DATABASE_URL=postgresql://terminal_user:password@localhost:5432/terminal_academy
DJANGO_SETTINGS_MODULE=core.settings.production
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com

# 4. Deploy
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 5. Run with Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Production (Docker)
```bash
# Configure production environment
cp .env.production.example .env.production
# Edit .env.production with real values

# Add SSL certificates to nginx/certs/
# - fullchain.pem
# - privkey.pem

# Deploy
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
```

## 🏗️ Architecture

```
terminal_academy/
├── core/              # Django project settings, URLs, Celery
├── users/             # Authentication, roles, permissions
├── courses/           # Course content, modules, lessons
├── labs/              # Terminal simulator (THE CORE FEATURE)
├── progress/          # XP, levels, achievements, streaks
├── security/          # Audit logs, rate limiting, IP blocking
├── templates/         # Django HTML templates
├── static/            # CSS, JavaScript
├── docs/              # Documentation (PostgreSQL setup, etc.)
├── nginx/             # Production reverse proxy
├── scripts/           # Deployment and maintenance scripts
├── Dockerfile         # Multi-stage production build
└── docker-compose.yml # Full stack deployment
```

## 🔐 Key Features

| Feature | Description |
|---------|-------------|
| **Simulated Terminal** | 30+ commands (nmap, curl, grep, etc.) with realistic output |
| **No Real Hacking** | 100% sandboxed - commands produce pre-configured responses |
| **Ethical Agreement** | Mandatory acceptance before accessing labs |
| **Role-Based Access** | Student, Mentor, Admin roles |
| **JWT + Session Auth** | Secure authentication with OTP support |
| **XP & Leveling** | Gamified learning with achievements |
| **Audit Logging** | Complete security trail |
| **Rate Limiting** | Database-based protection (PythonAnywhere compatible) |

## 🗄️ Database Options

- **Development**: SQLite (default, zero config)
- **Production**: PostgreSQL (recommended, scalable)
- **Switch environments**: Use `DJANGO_SETTINGS_MODULE` environment variable

See [docs/POSTGRESQL_SETUP_GUIDE.md](docs/POSTGRESQL_SETUP_GUIDE.md) for complete setup instructions.

## 🛡️ Security

- All terminal commands are simulated - no real execution
- Mandatory ethical hacking agreement
- Password complexity requirements (12+ chars)
- Account lockout after failed attempts
- CSRF/XSS protection enabled
- Rate limiting on sensitive endpoints
- Comprehensive audit logging
- IP blocking capabilities

## 📚 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register/` | User registration |
| `POST /api/v1/auth/login/` | Login (returns JWT) |
| `GET /api/v1/courses/` | List courses |
| `GET /api/v1/labs/` | List available labs |
| `POST /api/v1/labs/{id}/execute/` | Execute command in lab |
| `GET /api/v1/progress/stats/` | User stats |

## 🧪 Tech Stack

- **Backend**: Python 3.11+, Django 5+, Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache**: Database-backed (PythonAnywhere compatible)
- **Web Server**: Gunicorn + Nginx + WhiteNoise
- **Container**: Docker + Docker Compose

## 📖 Documentation

- [PostgreSQL Setup Guide](docs/POSTGRESQL_SETUP_GUIDE.md) - Complete production database setup
- [PostgreSQL Quick Start](docs/POSTGRESQL_QUICKSTART.md) - 5-minute team reference

## 📝 License

MIT License - See LICENSE file for details.

---

**Built for education. Use responsibly.** 🎓
