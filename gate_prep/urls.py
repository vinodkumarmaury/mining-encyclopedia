from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection

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

def migration_check(request):
    """Check migration status and run migrations if needed"""
    try:
        from django.core.management import execute_from_command_line
        from django.core.management.commands.migrate import Command as MigrateCommand
        from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
        from io import StringIO
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            # Show current migration status
            execute_from_command_line(['manage.py', 'showmigrations'])
            migration_status = mystdout.getvalue()
            
            # Reset stdout capture
            mystdout = StringIO()
            sys.stdout = mystdout
            
            # Run migrations
            execute_from_command_line(['manage.py', 'migrate'])
            migration_output = mystdout.getvalue()
            
        finally:
            sys.stdout = old_stdout
        
        return JsonResponse({
            'migration_status': migration_status,
            'migration_output': migration_output,
            'success': True
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('tests/', include('tests.urls', namespace='tests')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('', include('main.urls', namespace='main')),
    path('health/', health_check, name='health_check'),
    path('migrate/', migration_check, name='migration_check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    # convenience redirect so /profile works (maps to accounts app)
    path('profile/', RedirectView.as_view(url='/accounts/profile/', permanent=False)),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('tests/', include('tests.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)