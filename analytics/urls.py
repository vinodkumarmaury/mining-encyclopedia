from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('api/performance/', views.performance_data, name='performance_data'),
    path('api/activity/', views.activity_data, name='activity_data'),
    path('recommendations/', views.recommendations, name='recommendations'),
]