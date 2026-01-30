#!/usr/bin/env python
"""
PostgreSQL Connection Test Script
==================================
This script verifies that your PostgreSQL database is properly configured
and Django can connect to it.

Usage:
    python scripts/test_postgres_connection.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')

try:
    import django
    django.setup()
except Exception as e:
    print(f"❌ Error setting up Django: {e}")
    print("\nMake sure you have:")
    print("1. Set DJANGO_SETTINGS_MODULE environment variable")
    print("2. Installed all dependencies: pip install -r requirements/base.txt")
    sys.exit(1)

from django.db import connection
from django.conf import settings
from django.core.management import call_command
import psycopg2


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")


def test_database_connection():
    """Test basic database connection"""
    print_header("Testing Database Connection")
    
    try:
        # Get database settings
        db_settings = settings.DATABASES['default']
        
        print_info(f"Database Engine: {db_settings['ENGINE']}")
        print_info(f"Database Name: {db_settings.get('NAME', 'Not configured')}")
        print_info(f"Database Host: {db_settings.get('HOST', 'localhost')}")
        print_info(f"Database Port: {db_settings.get('PORT', '5432')}")
        print_info(f"Database User: {db_settings.get('USER', 'Not configured')}")
        
        # Check if using PostgreSQL
        if 'postgresql' not in db_settings['ENGINE']:
            print_warning("Database engine is not PostgreSQL!")
            print_info(f"Current engine: {db_settings['ENGINE']}")
            if 'sqlite' in db_settings['ENGINE']:
                print_info("You are using SQLite (development mode)")
            return False
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print_success("Successfully connected to PostgreSQL!")
            print_info(f"PostgreSQL Version: {version}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        print("\nTroubleshooting:")
        print("1. Check that PostgreSQL is running")
        print("2. Verify DATABASE_URL in .env file")
        print("3. Ensure database and user exist")
        print("4. Check credentials (username/password)")
        return False


def test_database_tables():
    """Test if Django tables exist"""
    print_header("Checking Database Tables")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE';
            """)
            table_count = cursor.fetchone()[0]
            
            if table_count == 0:
                print_warning("No tables found in database!")
                print_info("You need to run: python manage.py migrate")
                return False
            else:
                print_success(f"Found {table_count} tables in database")
                
                # List some tables
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    LIMIT 10;
                """)
                tables = cursor.fetchall()
                print_info("Sample tables:")
                for table in tables:
                    print(f"   - {table[0]}")
                
                return True
                
    except Exception as e:
        print_error(f"Error checking tables: {e}")
        return False


def test_django_check():
    """Run Django system check"""
    print_header("Running Django System Check")
    
    try:
        call_command('check', '--database', 'default', verbosity=0)
        print_success("Django system check passed!")
        return True
    except Exception as e:
        print_error(f"Django system check failed: {e}")
        return False


def test_model_query():
    """Test querying a Django model"""
    print_header("Testing Django ORM")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_count = User.objects.count()
        print_success(f"Successfully queried User model: {user_count} users found")
        
        if user_count > 0:
            latest_user = User.objects.latest('date_joined')
            print_info(f"Latest user: {latest_user.username} (joined: {latest_user.date_joined})")
        else:
            print_info("No users in database. Create one with: python manage.py createsuperuser")
        
        return True
        
    except Exception as e:
        print_error(f"Error querying models: {e}")
        print_info("You may need to run migrations: python manage.py migrate")
        return False


def test_cache():
    """Test cache configuration"""
    print_header("Testing Cache Configuration")
    
    try:
        from django.core.cache import cache
        
        # Test cache set/get
        test_key = 'postgres_test_key'
        test_value = 'Hello PostgreSQL!'
        
        cache.set(test_key, test_value, 60)
        retrieved = cache.get(test_key)
        
        if retrieved == test_value:
            print_success("Cache is working correctly!")
            cache.delete(test_key)
            return True
        else:
            print_error("Cache test failed: value mismatch")
            return False
            
    except Exception as e:
        print_error(f"Cache test failed: {e}")
        print_info("You may need to create cache table: python manage.py createcachetable")
        return False


def check_migrations():
    """Check if there are unapplied migrations"""
    print_header("Checking Migrations")
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print_warning(f"There are {len(plan)} unapplied migrations!")
            print_info("Run: python manage.py migrate")
            return False
        else:
            print_success("All migrations are applied!")
            return True
            
    except Exception as e:
        print_error(f"Error checking migrations: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests == 0:
        print_success("\n🎉 All tests passed! Your PostgreSQL setup is working correctly!")
    else:
        print_warning(f"\n⚠️  {failed_tests} test(s) failed. Please review the errors above.")
        print("\nNext steps:")
        print("1. Review the error messages above")
        print("2. Check docs/POSTGRESQL_SETUP_GUIDE.md for troubleshooting")
        print("3. Ensure PostgreSQL is running and DATABASE_URL is correct")
    
    return failed_tests == 0


def main():
    """Run all tests"""
    print_header("PostgreSQL Connection Test for Terminal Academy")
    print(f"\nSettings Module: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not Set')}")
    print(f"DEBUG Mode: {settings.DEBUG}")
    
    # Run tests
    results = {
        'Database Connection': test_database_connection(),
        'Database Tables': test_database_tables(),
        'Django System Check': test_django_check(),
        'Migrations Status': check_migrations(),
        'Django ORM': test_model_query(),
        'Cache Configuration': test_cache(),
    }
    
    # Print summary
    success = print_summary(results)
    
    if success:
        print("\n" + "=" * 70)
        print("  Next steps:")
        print("=" * 70)
        print("1. Create a superuser (if not done): python manage.py createsuperuser")
        print("2. Collect static files: python manage.py collectstatic --noinput")
        print("3. Run the development server: python manage.py runserver")
        print("4. Or deploy with Gunicorn: gunicorn core.wsgi:application")
        print("=" * 70)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
