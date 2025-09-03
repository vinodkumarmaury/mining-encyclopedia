#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Show database configuration
echo "🔍 Database configuration check..."
python -c "
import os
import dj_database_url
from django.conf import settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gate_prep.settings')
django.setup()
from django.db import connection

print('=' * 50)
print('DATABASE CONFIGURATION')
print('=' * 50)
database_url = os.environ.get('DATABASE_URL')
print(f'DATABASE_URL set: {bool(database_url)}')
if database_url:
    print(f'DATABASE_URL type: {database_url.split(\"://\")[0] if \"://\" in database_url else \"Unknown\"}')
    print(f'DATABASE_URL length: {len(database_url)}')

print(f'Database ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'Database NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'Database HOST: {settings.DATABASES[\"default\"].get(\"HOST\", \"Not set\")}')

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        version = cursor.fetchone()
        print(f'✅ Database connected: {version[0][:50]}...')
except Exception as e:
    print(f'❌ Database connection error: {e}')
print('=' * 50)
"

# Create any missing migrations
echo "🔄 Making migrations..."
python manage.py makemigrations

# Show migration status before running
echo "📋 Migration status BEFORE:"
python manage.py showmigrations --verbosity=0

# Run migrations with verbose output
echo "🔄 Running database migrations..."
python manage.py migrate --verbosity=2

# Show migration status after running
echo "✅ Migration status AFTER:"
python manage.py showmigrations --verbosity=0

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Check if database is working
echo "🔍 Checking database deployment..."
python manage.py check --deploy

# Load sample data
echo "📊 Loading sample data..."
python load_sample_data.py || echo "⚠️ Sample data loading failed, continuing..."

# Final verification
echo "🔍 Final database verification..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gate_prep.settings')
django.setup()

try:
    from main.models import Subject, Topic, Article
    from tests.models import MockTest
    from accounts.models import UserProfile
    
    print('=' * 50)
    print('DATABASE TABLES VERIFICATION')
    print('=' * 50)
    print(f'✅ Subjects: {Subject.objects.count()}')
    print(f'✅ Topics: {Topic.objects.count()}')
    print(f'✅ Articles: {Article.objects.count()}')
    print(f'✅ Tests: {MockTest.objects.count()}')
    print(f'✅ User Profiles: {UserProfile.objects.count()}')
    
    # Test a complex query
    if Article.objects.exists():
        test_article = Article.objects.select_related('topic__subject', 'author').first()
        print(f'✅ Complex query test: {test_article.title[:30]}...')
    
    print('=' * 50)
    print('🎉 All database checks passed!')
    
except Exception as e:
    print(f'❌ Database verification failed: {e}')
    import traceback
    traceback.print_exc()
"

echo "🎉 Build process completed successfully!"
