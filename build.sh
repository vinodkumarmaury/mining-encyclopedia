#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Show database configuration
echo "Database configuration check..."
python -c "
import os
import dj_database_url
from django.conf import settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gate_prep.settings')
django.setup()
from django.db import connection
print(f'Database ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'Database NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'DATABASE_URL set: {bool(os.environ.get(\"DATABASE_URL\"))}')
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        version = cursor.fetchone()
        print(f'Database version: {version[0]}')
except Exception as e:
    print(f'Database connection error: {e}')
"

# Make migrations if needed
echo "Making migrations..."
python manage.py makemigrations

# Show migration status before running
echo "Migration status before running:"
python manage.py showmigrations

# Run migrations
echo "Running database migrations..."
python manage.py migrate --verbosity=2

# Show migration status after running
echo "Migration status after running:"
python manage.py showmigrations

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Check if database is working
echo "Checking database deployment..."
python manage.py check --deploy

# Load sample data if needed (optional)
echo "Loading sample data..."
python load_sample_data.py || echo "Sample data loading failed, continuing..."

# Final check - show table counts
echo "Final database check..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gate_prep.settings')
django.setup()
from main.models import Subject, Topic, Article
from tests.models import MockTest
try:
    print(f'Subjects: {Subject.objects.count()}')
    print(f'Topics: {Topic.objects.count()}')
    print(f'Articles: {Article.objects.count()}')
    print(f'Tests: {MockTest.objects.count()}')
except Exception as e:
    print(f'Model check error: {e}')
"

echo "Build process completed successfully!"
