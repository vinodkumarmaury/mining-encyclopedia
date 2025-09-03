from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, F
from .models import MockTest, Question, TestAttempt, Answer, Leaderboard
from main.models import Subject, Topic
import json
from datetime import timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from django.contrib.auth.decorators import user_passes_test
from .forms import MockTestCreateForm


def is_student(user):
    try:
        return user.userprofile.role == 'student'
    except Exception:
        return False

def test_list(request):
    tests = MockTest.objects.filter(is_active=True)
    subjects = Subject.objects.all()
    
    # Filtering
    subject_filter = request.GET.get('subject')
    difficulty_filter = request.GET.get('difficulty')
    
    if subject_filter:
        tests = tests.filter(subject_id=subject_filter)
    
    if difficulty_filter:
        tests = tests.filter(difficulty=difficulty_filter)
    
    context = {
        'tests': tests,
        'subjects': subjects,
        'current_subject': int(subject_filter) if subject_filter else None,
        'current_difficulty': difficulty_filter,
    }
    return render(request, 'tests/test_list.html', context)

def test_detail(request, test_id):
    test = get_object_or_404(MockTest, id=test_id, is_active=True)
    user_attempts = []
    
    if request.user.is_authenticated:
        user_attempts = TestAttempt.objects.filter(
            user=request.user, 
            mock_test=test,
            is_completed=True
        )[:5]
    
    context = {
        'test': test,
        'user_attempts': user_attempts,
    }
    return render(request, 'tests/test_detail.html', context)

@login_required
@user_passes_test(is_student)
def start_test(request, test_id):
    test = get_object_or_404(MockTest, id=test_id, is_active=True)
    
    # Check for incomplete attempts
    incomplete_attempt = TestAttempt.objects.filter(
        user=request.user,
        mock_test=test,
        is_completed=False
    ).first()
    
    if incomplete_attempt:
        return redirect('tests:take_test', attempt_id=incomplete_attempt.id)
    
    # Create new attempt
    attempt = TestAttempt.objects.create(
        user=request.user,
        mock_test=test
    )
    
    return redirect('tests:take_test', attempt_id=attempt.id)

@login_required
@user_passes_test(is_student)
def take_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    if attempt.is_completed:
        return redirect('tests:test_results', attempt_id=attempt.id)
    
    questions = attempt.mock_test.questions.all()
    
    # Get existing answers
    existing_answers = {
        answer.question.id: answer.user_answer 
        for answer in attempt.answers.all()
    }
    
    context = {
        'attempt': attempt,
        'questions': questions,
        'existing_answers': existing_answers,
    }
    return render(request, 'tests/take_test.html', context)

@login_required
@user_passes_test(is_student)
@require_POST
def submit_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    if attempt.is_completed:
        return JsonResponse({'error': 'Test already completed'})
    
    # Process answers
    total_score = 0
    correct_answers = 0
    
    for question in attempt.mock_test.questions.all():
        user_answer = request.POST.get(f'question_{question.id}', '')
        
        # Check if answer is correct
        is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
        marks_obtained = question.marks if is_correct else 0
        
        if is_correct:
            correct_answers += 1
            total_score += marks_obtained
        
        # Save or update answer
        Answer.objects.update_or_create(
            test_attempt=attempt,
            question=question,
            defaults={
                'user_answer': user_answer,
                'is_correct': is_correct,
                'marks_obtained': marks_obtained,
            }
        )
    
    # Update attempt
    attempt.completed_at = timezone.now()
    attempt.total_score = total_score
    attempt.percentage = (total_score / attempt.mock_test.total_marks) * 100
    attempt.time_taken_minutes = int((attempt.completed_at - attempt.started_at).total_seconds() / 60)
    attempt.is_completed = True
    attempt.save()
    
    # Update user profile
    profile = request.user.userprofile
    profile.total_tests_taken += 1
    profile.save()
    
    # Update leaderboard
    update_leaderboard(request.user)
    
    return JsonResponse({
        'success': True,
        'redirect_url': f'/tests/results/{attempt.id}/'
    })

@login_required
def test_results(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    if not attempt.is_completed:
        return redirect('tests:take_test', attempt_id=attempt.id)
    
    answers = attempt.answers.all().select_related('question')
    correct_count = answers.filter(is_correct=True).count()
    total_questions = answers.count()
    
    # Subject-wise performance
    subject_performance = {}
    for answer in answers:
        subject_name = answer.question.topic.subject.name
        if subject_name not in subject_performance:
            subject_performance[subject_name] = {'correct': 0, 'total': 0}
        
        subject_performance[subject_name]['total'] += 1
        if answer.is_correct:
            subject_performance[subject_name]['correct'] += 1
    
    # Calculate percentages
    for subject in subject_performance:
        total = subject_performance[subject]['total']
        correct = subject_performance[subject]['correct']
        subject_performance[subject]['percentage'] = (correct / total) * 100 if total > 0 else 0
    
    context = {
        'attempt': attempt,
        'answers': answers,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'subject_performance': subject_performance,
    }
    return render(request, 'tests/test_results.html', context)

def leaderboard(request):
    leaderboard_data = Leaderboard.objects.select_related('user').all()[:50]
    
    context = {'leaderboard': leaderboard_data}
    return render(request, 'tests/leaderboard.html', context)

def update_leaderboard(user):
    attempts = TestAttempt.objects.filter(user=user, is_completed=True)
    
    if attempts.exists():
        total_score = sum(attempt.total_score for attempt in attempts)
        tests_completed = attempts.count()
        average_percentage = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
        
        leaderboard, created = Leaderboard.objects.get_or_create(
            user=user,
            defaults={
                'total_score': total_score,
                'tests_completed': tests_completed,
                'average_percentage': average_percentage,
            }
        )
        
        if not created:
            leaderboard.total_score = total_score
            leaderboard.tests_completed = tests_completed
            leaderboard.average_percentage = average_percentage
            leaderboard.save()


def is_professor(user):
    try:
        return user.userprofile.role == 'professor' or user.is_staff
    except Exception:
        return user.is_staff



@login_required
@user_passes_test(is_professor)
def create_test(request):
    if request.method == 'POST':
        form = MockTestCreateForm(request.POST)
        if form.is_valid():
            mt = form.save()
            messages.success(request, 'Mock test created successfully!')
            return redirect('tests:test_detail', test_id=mt.id)
    else:
        form = MockTestCreateForm()

    return render(request, 'tests/create_test.html', {'form': form})

@login_required
def export_pdf(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content
    p.drawString(100, 750, f"GATE Mining Prep - Test Results")
    p.drawString(100, 720, f"Test: {attempt.mock_test.title}")
    p.drawString(100, 690, f"Student: {attempt.user.get_full_name() or attempt.user.username}")
    p.drawString(100, 660, f"Score: {attempt.total_score}/{attempt.mock_test.total_marks}")
    p.drawString(100, 630, f"Percentage: {attempt.percentage:.1f}%")
    p.drawString(100, 600, f"Time Taken: {attempt.time_taken_minutes} minutes")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="test_result_{attempt.id}.pdf"'
    
    return response