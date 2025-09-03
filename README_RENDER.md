Deploying to Render (quickstart)

1. Create a new Web Service on Render and connect your repository.

2. Set the build and start commands (render.yaml / Procfile provided):
   - Build command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   - Start command: gunicorn gate_prep.wsgi:application --bind 0.0.0.0:$PORT

3. Add environment variables on Render:
   - SECRET_KEY (required)
   - DATABASE_URL (use Render PostgreSQL addon or external DB)
   - DEBUG=false
   - SITE_ADMIN_CODE (optional admin promotion code)

4. After deploy, open the Live URL and create a superuser:
   - You can use Render's shell or run `python manage.py createsuperuser` via their console

Notes:
- Use PostgreSQL in production; SQLite is for local/dev only.
- Make sure `STATICFILES_STORAGE` and Whitenoise are configured in `gate_prep/settings.py` (already done).
- Keep secrets out of the repo; use the Render dashboard to set env vars.
