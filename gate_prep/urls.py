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

def debug_view(request):
    """Debug view to check database tables and models"""
    try:
        from django.apps import apps
        from main.models import Article, Subject, Topic
        from tests.models import MockTest
        
        info = {
            'tables_exist': True,
            'models': {},
            'errors': []
        }
        
        try:
            info['models']['subjects'] = Subject.objects.count()
        except Exception as e:
            info['errors'].append(f"Subject model error: {str(e)}")
            
        try:
            info['models']['topics'] = Topic.objects.count()
        except Exception as e:
            info['errors'].append(f"Topic model error: {str(e)}")
            
        try:
            info['models']['articles'] = Article.objects.count()
        except Exception as e:
            info['errors'].append(f"Article model error: {str(e)}")
            
        try:
            info['models']['tests'] = MockTest.objects.count()
        except Exception as e:
            info['errors'].append(f"MockTest model error: {str(e)}")
        
        return JsonResponse(info)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'type': type(e).__name__
        })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('tests/', include('tests.urls', namespace='tests')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('', include('main.urls', namespace='main')),
    path('health/', health_check, name='health_check'),
    path('debug/', debug_view, name='debug_view'),
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