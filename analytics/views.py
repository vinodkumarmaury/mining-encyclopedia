from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from main.models import Article, Subject
from tests.models import MockTest, TestAttempt, Question
from accounts.models import UserProfile
import json

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def analytics_dashboard(request):
    # Basic stats
    total_users = User.objects.count()
    total_articles = Article.objects.filter(is_published=True).count()
    total_tests = MockTest.objects.filter(is_active=True).count()
    total_attempts = TestAttempt.objects.filter(is_completed=True).count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_attempts = TestAttempt.objects.filter(is_completed=True).order_by('-completed_at')[:10]
    
    # Popular content
    popular_articles = Article.objects.filter(is_published=True).order_by('-views')[:10]
    popular_tests = MockTest.objects.annotate(
        attempt_count=Count('testattempt')
    ).order_by('-attempt_count')[:10]
    
    context = {
        'total_users': total_users,
        'total_articles': total_articles,
        'total_tests': total_tests,
        'total_attempts': total_attempts,
        'recent_users': recent_users,
        'recent_attempts': recent_attempts,
        'popular_articles': popular_articles,
        'popular_tests': popular_tests,
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required
def performance_data(request):
    user = request.user
    attempts = TestAttempt.objects.filter(user=user, is_completed=True).order_by('completed_at')
    
    data = {
        'dates': [attempt.completed_at.strftime('%Y-%m-%d') for attempt in attempts],
        'scores': [float(attempt.percentage) for attempt in attempts],
        'subjects': [],
    }
    
    # Subject-wise performance
    subjects = Subject.objects.all()
    for subject in subjects:
        subject_attempts = attempts.filter(mock_test__subject=subject)
        if subject_attempts.exists():
            avg_score = subject_attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
            data['subjects'].append({
                'name': subject.name,
                'average': round(avg_score, 1),
                'attempts': subject_attempts.count()
            })
    
    return JsonResponse(data)

@login_required
def activity_data(request):
    # Last 30 days activity
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    activity = []
    current_date = start_date
    
    while current_date <= end_date:
        day_attempts = TestAttempt.objects.filter(
            user=request.user,
            completed_at__date=current_date,
            is_completed=True
        ).count()
        
        activity.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'attempts': day_attempts
        })
        
        current_date += timedelta(days=1)
    
    return JsonResponse({'activity': activity})

@login_required
def recommendations(request):
    user = request.user
    
    # Get weak subjects based on test performance
    weak_subjects = []
    subject_performance = {}
    
    attempts = TestAttempt.objects.filter(user=user, is_completed=True)
    
    for attempt in attempts:
        subject = attempt.mock_test.subject
        if subject.id not in subject_performance:
            subject_performance[subject.id] = {
                'subject': subject,
                'total_score': 0,
                'total_attempts': 0
            }
        
        subject_performance[subject.id]['total_score'] += attempt.percentage
        subject_performance[subject.id]['total_attempts'] += 1
    
    # Calculate averages and find weak areas
    for subject_id, data in subject_performance.items():
        avg_percentage = data['total_score'] / data['total_attempts']
        if avg_percentage < 60:  # Consider below 60% as weak
            weak_subjects.append(data['subject'])
    
    # Recommend articles and tests for weak subjects
    recommended_articles = Article.objects.filter(
        topic__subject__in=weak_subjects,
        is_published=True
    )[:10]
    
    recommended_tests = MockTest.objects.filter(
        subject__in=weak_subjects,
        is_active=True
    )[:5]
    
    context = {
        'weak_subjects': weak_subjects,
        'recommended_articles': recommended_articles,
        'recommended_tests': recommended_tests,
    }
    return render(request, 'analytics/recommendations.html', context)