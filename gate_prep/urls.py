from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection
import os

def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        'status': 'healthy',
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'database': db_status,
    })

def env_check(request):
    """Check environment variables and database configuration"""
    database_url = os.environ.get('DATABASE_URL')
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    
    # Get database configuration
    db_config = settings.DATABASES['default']
    
    env_info = {
        'DATABASE_URL_set': bool(database_url),
        'DATABASE_URL_length': len(database_url) if database_url else 0,
        'RENDER_EXTERNAL_HOSTNAME': render_hostname,
        'database_engine': db_config.get('ENGINE'),
        'database_name': str(db_config.get('NAME')),
        'database_host': db_config.get('HOST', 'Not set'),
        'database_port': db_config.get('PORT', 'Not set'),
    }
    
    # Test actual database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            env_info['database_version'] = version[0] if version else 'Unknown'
            
            # Try to list tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            env_info['existing_tables'] = tables
            
    except Exception as e:
        env_info['database_error'] = str(e)
    
    return JsonResponse(env_info, indent=2)

def collectstatic_force(request):
    """Force collect static files - emergency tool"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        output = StringIO()
        call_command('collectstatic', '--noinput', '--clear', verbosity=2, stdout=output)
        result = output.getvalue()
        
        return JsonResponse({
            'status': 'success',
            'output': result[:1000],  # Limit output size
            'message': 'Static files collected successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('env/', env_check, name='env_check'),
    path('collectstatic/', collectstatic_force, name='collectstatic_force'),
    path('admin/', admin.site.urls),
    path('profile/', RedirectView.as_view(url='/accounts/profile/', permanent=False)),
    path('', include('main.urls', namespace='main')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('tests/', include('tests.urls', namespace='tests')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)