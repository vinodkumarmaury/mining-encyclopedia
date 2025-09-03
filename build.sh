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

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Check if database is working
echo "Checking database..."
python manage.py check --deploy

# Create superuser if it doesn't exist (optional - for demo purposes)
# Uncomment the next line if you want to auto-create admin user
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')"

# Load sample data if needed (optional)
echo "Loading sample data..."
python load_sample_data.py || echo "Sample data loading failed, continuing..."

echo "Build process completed successfully!"
