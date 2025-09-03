from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Article, Subject, Topic, Bookmark, Note
from .forms import ArticleCreateForm
from tests.models import TestAttempt, MockTest
from accounts.models import UserProfile
import json
from django.utils import timezone

def home(request):
    featured_articles = Article.objects.filter(is_published=True)[:6]
    featured_tests = MockTest.objects.filter(is_featured=True, is_active=True)[:4]
    subjects = Subject.objects.all()[:6]
    
    context = {
        'featured_articles': featured_articles,
        'featured_tests': featured_tests,
        'subjects': subjects,
    }
    return render(request, 'main/home.html', context)

@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    recent_attempts = TestAttempt.objects.filter(user=request.user, is_completed=True)[:5]
    bookmarked_articles = Article.objects.filter(bookmark__user=request.user)[:5]
    
    # Performance statistics
    total_tests = TestAttempt.objects.filter(user=request.user, is_completed=True).count()
    avg_score = TestAttempt.objects.filter(user=request.user, is_completed=True).aggregate(
        avg_score=Avg('percentage')
    )['avg_score'] or 0
    
    # Recent activity
    recent_activity = []
    for attempt in recent_attempts:
        recent_activity.append({
            'type': 'test',
            'title': attempt.mock_test.title,
            'score': attempt.percentage,
            'date': attempt.completed_at
        })
    
    context = {
        'user_profile': user_profile,
        'recent_attempts': recent_attempts,
        'bookmarked_articles': bookmarked_articles,
        'total_tests': total_tests,
        'avg_score': round(avg_score, 1),
        'recent_activity': recent_activity,
    }
    return render(request, 'main/dashboard.html', context)


@login_required
def article_create(request):
    # Only professors or staff can create articles
    try:
        if request.user.userprofile.role != 'professor' and not request.user.is_staff:
            messages.error(request, 'You do not have permission to create articles.')
            return redirect('main:dashboard')
    except Exception:
        return redirect('main:dashboard')

    if request.method == 'POST':
        form = ArticleCreateForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully.')
            return redirect('main:article_detail', slug=article.slug)
    else:
        form = ArticleCreateForm()

    return render(request, 'main/article_create.html', {'form': form})

def article_list(request):
    from django.core.paginator import Paginator
    articles_qs = Article.objects.filter(is_published=True)
    subjects = Subject.objects.all()
    difficulties = Article.DIFFICULTY_CHOICES
    
    # Filtering
    subject_filter = request.GET.get('subject')
    difficulty_filter = request.GET.get('difficulty')
    search_query = request.GET.get('search')
    bookmarked_filter = request.GET.get('bookmarked')
    
    if subject_filter:
        articles_qs = articles_qs.filter(topic__subject_id=subject_filter)
    
    if difficulty_filter:
        articles_qs = articles_qs.filter(difficulty=difficulty_filter)
    
    if search_query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Bookmarks filter - only for authenticated users
    if bookmarked_filter and request.user.is_authenticated:
        articles_qs = articles_qs.filter(bookmark__user=request.user)

    # Pagination
    paginator = Paginator(articles_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    articles = page_obj.object_list
    
    context = {
        'articles': articles,
        'subjects': subjects,
        'difficulties': difficulties,
        'current_subject': int(subject_filter) if subject_filter else None,
        'current_difficulty': difficulty_filter,
        'search_query': search_query,
        'bookmarked_filter': bookmarked_filter,
        'page_obj': page_obj,
    }
    return render(request, 'main/article_list.html', context)

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Increment view count
    article.views += 1
    article.save()
    
    # Check if bookmarked (for authenticated users)
    is_bookmarked = False
    user_note = None
    
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, article=article).exists()
        try:
            user_note = Note.objects.get(user=request.user, article=article)
        except Note.DoesNotExist:
            user_note = None
    
    # Related articles
    related_articles = Article.objects.filter(
        topic=article.topic, 
        is_published=True
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'is_bookmarked': is_bookmarked,
        'user_note': user_note,
        'related_articles': related_articles,
    }
    return render(request, 'main/article_detail.html', context)

def article_search(request):
    query = request.GET.get('q', '')
    articles = []
    
    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query),
            is_published=True
        )[:10]
    
    results = [{
        'id': article.id,
        'title': article.title,
        'excerpt': article.excerpt,
        'url': f'/articles/{article.slug}/',
        'difficulty': article.get_difficulty_display(),
        'topic': article.topic.name
    } for article in articles]
    
    return JsonResponse({'results': results})

@login_required
@require_POST
def toggle_bookmark(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user, 
        article=article
    )
    
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    
    return JsonResponse({'bookmarked': bookmarked})

@login_required
@require_POST
def save_note(request):
    article_id = request.POST.get('article_id')
    content = request.POST.get('content')
    
    article = get_object_or_404(Article, id=article_id)
    note, created = Note.objects.get_or_create(
        user=request.user,
        article=article,
        defaults={'content': content}
    )
    
    if not created:
        note.content = content
        note.save()
    
    return JsonResponse({'success': True})

def subject_list(request):
    subjects = Subject.objects.annotate(
        article_count=Count('topics__articles'),
        test_count=Count('mock_tests')
    )
    
    context = {'subjects': subjects}
    return render(request, 'main/subject_list.html', context)

def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    topics = subject.topics.all()
    articles = Article.objects.filter(topic__subject=subject, is_published=True)[:10]
    tests = MockTest.objects.filter(subject=subject, is_active=True)[:5]
    
    context = {
        'subject': subject,
        'topics': topics,
        'articles': articles,
        'tests': tests,
    }
    return render(request, 'main/subject_detail.html', context)

@login_required
def bookmarks_api(request):
    """API endpoint to fetch user's bookmarks for the navigation dropdown"""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('article', 'article__topic', 'article__topic__subject').order_by('-created_at')[:10]
    
    bookmarks_data = []
    for bookmark in bookmarks:
        article = bookmark.article
        bookmarks_data.append({
            'id': bookmark.id,
            'created_at': bookmark.created_at.strftime('%b %d'),
            'article': {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'excerpt': article.excerpt or article.content[:100] + '...' if len(article.content) > 100 else article.content,
                'subject': article.topic.subject.name,
                'difficulty': article.get_difficulty_display(),
                'views': article.views,
            }
        })
    
    return JsonResponse({
        'bookmarks': bookmarks_data,
        'count': len(bookmarks_data)
    })