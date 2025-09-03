#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Create persistent disk directory if it doesn't exist
if [ ! -z "$RENDER_EXTERNAL_HOSTNAME" ]; then
    echo "Creating persistent disk directory..."
    mkdir -p /opt/render/project/data
    ls -la /opt/render/project/data || echo "Persistent disk directory not accessible"
fi

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if database file exists
echo "Checking database file..."
if [ ! -z "$RENDER_EXTERNAL_HOSTNAME" ] && [ -d "/opt/render/project/data" ]; then
    echo "Using persistent disk for database"
    ls -la /opt/render/project/data/db.sqlite3 || echo "Database file doesn't exist on persistent disk yet"
else
    echo "Using local directory for database"
    ls -la db.sqlite3 || echo "Database file doesn't exist yet"
fi

# Make migrations if needed
echo "Making migrations..."
python manage.py makemigrations

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Show migration status
echo "Migration status:"
python manage.py showmigrations

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Check if database is working
echo "Checking database..."
python manage.py check --deploy

# Load sample data if needed (optional)
echo "Loading sample data..."
python load_sample_data.py || echo "Sample data loading failed, continuing..."

echo "Final database file status:"
if [ ! -z "$RENDER_EXTERNAL_HOSTNAME" ] && [ -d "/opt/render/project/data" ]; then
    ls -la /opt/render/project/data/db.sqlite3 || echo "Database file missing on persistent disk"
else
    ls -la db.sqlite3 || echo "Database file missing in local directory"
fi

echo "Build process completed successfully!"
