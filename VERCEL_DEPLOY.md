# Deploying Terminal Academy to Vercel

## Prerequisites

1. [Vercel account](https://vercel.com/signup)
2. [Vercel CLI](https://vercel.com/docs/cli) installed: `npm i -g vercel`
3. [Neon](https://neon.tech) or [Supabase](https://supabase.com) account for PostgreSQL

---

## Step 1: Set up PostgreSQL Database

Vercel is serverless and doesn't support SQLite (filesystem is ephemeral). You need an external PostgreSQL database.

### Option A: Neon (Recommended - Free tier available)

1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project
3. Create a database
4. Get the connection string (format: `postgres://user:password@host:port/database`)

### Option B: Supabase

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings > Database > Connection String
4. Copy the URI connection string

---

## Step 2: Deploy to Vercel

### Initial Setup

```bash
# Login to Vercel
vercel login

# Go to your project directory
cd C:\Users\Dialga\OneDrive\Documents\Terminal_acadmy-main

# Deploy
vercel
```

### Set Environment Variables

```bash
# Required - Get this from your database provider
vercel env add DATABASE_URL
# Enter your PostgreSQL connection string

# Optional but recommended
vercel env add SECRET_KEY
# Generate a new secure key: python -c "import secrets; print(secrets.token_urlsafe(50))"

vercel env add DEBUG
# Enter: false
```

---

## Step 3: Run Migrations

After the initial deployment, you need to run migrations. There are two options:

### Option A: Using Vercel Shell (Recommended)

```bash
# Connect to your deployment
vercel --prod

# Open a shell
vercel shell

# Run migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

### Option B: Local with Database Connection

```bash
# Set the DATABASE_URL locally
export DATABASE_URL="your-neon-connection-string"

# Run migrations from your local machine
python manage.py migrate
```

---

## Step 4: Verify Deployment

1. Go to your Vercel dashboard
2. Find your project URL (e.g., `https://terminal-academy-xyz.vercel.app`)
3. Visit the admin panel: `https://terminal-academy-xyz.vercel.app/admin/`
4. Log in with your superuser credentials

---

## Troubleshooting

### Build Fails

```bash
# Check build logs
vercel --prod

# Or check in Vercel dashboard > Deployments > Latest > Build Logs
```

### Database Connection Error

- Verify `DATABASE_URL` is set correctly in Vercel environment variables
- Make sure your database allows connections from Vercel's IPs
- For Neon: Check that your database is active (not paused)

### Static Files Not Loading

- Ensure `collectstatic` ran successfully during build
- Check that `staticfiles` directory is created

### "DisallowedHost" Error

- Add your Vercel domain to `ALLOWED_HOSTS` in environment variables
- Format: `*.vercel.app,your-domain.vercel.app`

### Migration Issues

If you get migration errors, connect to your database and run:

```bash
python manage.py migrate --run-syncdb
```

---

## Files Changed for Vercel

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel deployment configuration |
| `vercel_wsgi.py` | WSGI entry point for serverless |
| `core/settings/vercel.py` | Vercel-specific Django settings |
| `build.sh` | Build script for Vercel |

---

## Important Notes

1. **Database**: SQLite won't work on Vercel. You MUST use PostgreSQL (Neon/Supabase/AWS RDS/etc.)

2. **Migrations**: Don't run during build phase. Run them after deployment using `vercel shell`

3. **Media Files**: For file uploads, consider using:
   - AWS S3
   - Cloudinary
   - Supabase Storage

4. **Free Tier Limits**:
   - Vercel: 100GB bandwidth, 1000 builds/month
   - Neon: 500MB storage, 190 compute hours/month
   - Supabase: 500MB storage, 2GB transfer

---

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify database connection
3. Ensure all environment variables are set
