from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('debug-db/', views.debug_db_status, name='debug_db_status'),
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