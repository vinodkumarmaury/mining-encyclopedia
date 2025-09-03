#!/usr/bin/env bash
# Release script: run migrations, collectstatic, and optionally create a superuser.
# Intended to be run by the hosting platform during deployment.
set -euo pipefail

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optionally create a default superuser when env var is provided
if [ -n "${CREATE_SUPERUSER:-}" ] && [ -n "${ADMIN_EMAIL:-}" ] && [ -n "${ADMIN_PASSWORD:-}" ]; then
  echo "Creating default superuser..."
  python - <<PY
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='${ADMIN_EMAIL}').exists():
    User.objects.create_superuser(username='${ADMIN_EMAIL}', email='${ADMIN_EMAIL}', password='${ADMIN_PASSWORD}')
    print('Superuser created')
else:
    print('Superuser already exists')
PY
fi

echo "Release tasks completed."
