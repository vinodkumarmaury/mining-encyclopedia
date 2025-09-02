from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('<int:test_id>/', views.test_detail, name='test_detail'),
    path('<int:test_id>/start/', views.start_test, name='start_test'),
    path('attempt/<int:attempt_id>/', views.take_test, name='take_test'),
    path('attempt/<int:attempt_id>/submit/', views.submit_test, name='submit_test'),
    path('results/<int:attempt_id>/', views.test_results, name='test_results'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('export/<int:attempt_id>/pdf/', views.export_pdf, name='export_pdf'),
    path('create/', views.create_test, name='create_test'),
]