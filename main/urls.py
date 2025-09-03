from django.urls import path
from . import views
from django.http import JsonResponse

def debug_db(request):
    """Quick database debug endpoint"""
    try:
        from django.db import connection
        from .models import Subject, Topic, Article
        from tests.models import MockTest
        
        info = {
            'database_connected': False,
            'tables_exist': {},
            'counts': {},
            'errors': []
        }
        
        # Test connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                info['database_connected'] = True
                info['database_version'] = version[0][:50] if version else 'Unknown'
        except Exception as e:
            info['errors'].append(f"Connection error: {str(e)}")
        
        # Test each model
        models_to_test = [
            ('Subject', Subject),
            ('Topic', Topic), 
            ('Article', Article),
            ('MockTest', MockTest)
        ]
        
        for name, model in models_to_test:
            try:
                count = model.objects.count()
                info['tables_exist'][name] = True
                info['counts'][name] = count
            except Exception as e:
                info['tables_exist'][name] = False
                info['errors'].append(f"{name}: {str(e)}")
        
        return JsonResponse(info, indent=2)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('debug-db/', debug_db, name='debug_db'),
    path('test/', views.test_simple, name='test_simple'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('articles/', views.article_list, name='article_list'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('articles/search/', views.article_search, name='article_search'),
    path('bookmark/<int:article_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('api/bookmarks/', views.bookmarks_api, name='bookmarks_api'),
    path('note/save/', views.save_note, name='save_note'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:subject_id>/', views.subject_detail, name='subject_detail'),
]