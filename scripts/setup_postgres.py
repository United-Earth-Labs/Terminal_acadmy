#!/usr/bin/env python
"""
Quick PostgreSQL Database Setup Script
========================================
This script automates the creation of the PostgreSQL database and user
for Terminal Academy.

Usage:
    python scripts/setup_postgres.py

Prerequisites:
    - PostgreSQL installed and running
    - psycopg2-binary installed (pip install psycopg2-binary)
"""

import sys
import os
import getpass
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}", file=sys.stderr)


def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")


def main():
    print_header("PostgreSQL Setup for Terminal Academy")
    
    # Get configuration
    print("\n📋 Please provide the following information:\n")
    
    # PostgreSQL superuser credentials
    pg_host = input("PostgreSQL host [localhost]: ").strip() or "localhost"
    pg_port = input("PostgreSQL port [5432]: ").strip() or "5432"
    pg_superuser = input("PostgreSQL superuser [postgres]: ").strip() or "postgres"
    pg_superuser_password = getpass.getpass("PostgreSQL superuser password: ")
    
    print()
    
    # New database configuration
    db_name = input("Database name [terminal_academy]: ").strip() or "terminal_academy"
    db_user = input("Database user [terminal_user]: ").strip() or "terminal_user"
    db_password = getpass.getpass(f"Password for user '{db_user}': ")
    db_password_confirm = getpass.getpass("Confirm password: ")
    
    if db_password != db_password_confirm:
        print_error("Passwords do not match!")
        sys.exit(1)
    
    print_header("Connecting to PostgreSQL")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            user=pg_superuser,
            password=pg_superuser_password,
            database="postgres"  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print_success(f"Connected to PostgreSQL at {pg_host}:{pg_port}")
        
        # Check if user exists
        print_header("Creating Database User")
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (db_user,)
        )
        user_exists = cursor.fetchone()
        
        if user_exists:
            print_warning(f"User '{db_user}' already exists. Skipping user creation.")
        else:
            # Create user
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(db_user)
                ),
                (db_password,)
            )
            print_success(f"Created user '{db_user}'")
        
        # Check if database exists
        print_header("Creating Database")
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        db_exists = cursor.fetchone()
        
        if db_exists:
            print_warning(f"Database '{db_name}' already exists.")
            overwrite = input("Do you want to drop and recreate it? (yes/no) [no]: ").strip().lower()
            
            if overwrite == "yes":
                cursor.execute(
                    sql.SQL("DROP DATABASE {}").format(sql.Identifier(db_name))
                )
                print_success(f"Dropped existing database '{db_name}'")
                db_exists = False
        
        if not db_exists:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(db_name),
                    sql.Identifier(db_user)
                )
            )
            print_success(f"Created database '{db_name}'")
        
        # Grant privileges
        print_header("Granting Privileges")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(db_name),
                sql.Identifier(db_user)
            )
        )
        print_success(f"Granted all privileges on '{db_name}' to '{db_user}'")
        
        # Connect to new database to grant schema privileges
        cursor.close()
        conn.close()
        
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            user=pg_superuser,
            password=pg_superuser_password,
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Grant schema privileges
        cursor.execute(
            sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
                sql.Identifier(db_user)
            )
        )
        cursor.execute(
            sql.SQL("GRANT ALL ON ALL TABLES IN SCHEMA public TO {}").format(
                sql.Identifier(db_user)
            )
        )
        cursor.execute(
            sql.SQL("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {}").format(
                sql.Identifier(db_user)
            )
        )
        print_success("Granted schema privileges")
        
        # Test connection
        print_header("Testing Connection")
        cursor.close()
        conn.close()
        
        test_conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        test_conn.close()
        print_success("Successfully connected to database as new user")
        
        # Generate DATABASE_URL
        print_header("Setup Complete!")
        print("\n🎉 PostgreSQL database setup successful!\n")
        print("Add this to your .env file:\n")
        print(f"DATABASE_URL=postgresql://{db_user}:{db_password}@{pg_host}:{pg_port}/{db_name}")
        print()
        print("Next steps:")
        print("1. Set DJANGO_SETTINGS_MODULE=core.settings.production")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py createcachetable")
        print("4. Run: python manage.py createsuperuser")
        print("5. Run: python manage.py runserver")
        print()
        
    except psycopg2.Error as e:
        print_error(f"PostgreSQL Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected Error: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(130)
