from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Article, Subject, Topic, Bookmark, Note
from .forms import ArticleCreateForm
from tests.models import TestAttempt, MockTest
from accounts.models import UserProfile
import json
from django.utils import timezone

def test_simple(request):
    """Simple test endpoint to check if views work"""
    return HttpResponse("✅ Main app views working correctly!")

def test_admin(request):
    """Test admin functionality without static files"""
    try:
        from django.contrib.admin import site
        from django.contrib.auth.models import User
        
        admin_info = {
            'admin_registered_models': len(site._registry),
            'user_count': User.objects.count(),
            'superuser_count': User.objects.filter(is_superuser=True).count(),
        }
        
        html = f"""
        <h1>🔧 Admin Test</h1>
        <p>Admin registry: {admin_info['admin_registered_models']} models</p>
        <p>Total users: {admin_info['user_count']}</p>
        <p>Superusers: {admin_info['superuser_count']}</p>
        <hr>
        <h3>🎯 Admin Access Options:</h3>
        <ol>
            <li><strong>Register via Frontend:</strong> <a href="/accounts/register/">Register as Admin</a> (use role: Admin)</li>
            <li><strong>Login:</strong> <a href="/accounts/login/">Login</a> once registered</li>
            <li><strong>Admin Panel:</strong> <a href="/admin/">Access Admin Panel</a></li>
        </ol>
        <p><a href="/">← Back to Home</a></p>
        """
        
        return HttpResponse(html)
        
    except Exception as e:
        return HttpResponse(f"Admin test error: {str(e)}", status=500)

def create_emergency_admin(request):
    """Emergency admin creation endpoint - for production deployment"""
    try:
        from django.contrib.auth.models import User
        from accounts.models import UserProfile
        
        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            return HttpResponse("""
                <h1>❌ Admin Already Exists</h1>
                <p>A superuser already exists in the system.</p>
                <p><a href="/admin/">Go to Admin Panel</a></p>
                <p><a href="/">← Back to Home</a></p>
            """)
        
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            email = request.POST.get('email', '').strip()
            
            if len(username) < 3 or len(password) < 6:
                return HttpResponse("""
                    <h1>❌ Invalid Input</h1>
                    <p>Username must be at least 3 characters, password at least 6 characters.</p>
                    <p><a href="/create-admin/">← Try Again</a></p>
                """)
            
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            # Create profile
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'admin'}
            )
            
            return HttpResponse(f"""
                <h1>✅ Emergency Admin Created!</h1>
                <p><strong>Username:</strong> {username}</p>
                <p><strong>Email:</strong> {email}</p>
                <p>You can now login to the admin panel.</p>
                <p><a href="/admin/">Go to Admin Panel</a></p>
                <p><a href="/">← Back to Home</a></p>
            """)
        
        # Show form
        return HttpResponse("""
            <h1>🚨 Emergency Admin Creation</h1>
            <p><strong>Warning:</strong> This creates a superuser account. Only use if no admin exists.</p>
            <form method="post">
                <p><label>Username: <input type="text" name="username" required minlength="3"></label></p>
                <p><label>Email: <input type="email" name="email" required></label></p>
                <p><label>Password: <input type="password" name="password" required minlength="6"></label></p>
                <p><button type="submit" style="background: red; color: white; padding: 10px;">CREATE ADMIN</button></p>
            </form>
            <p><a href="/">← Back to Home</a></p>
        """)
        
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

def debug_db_status(request):
    """Quick database debug endpoint"""
    try:
        # Test basic database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            
        # Test if we can import models
        count = Subject.objects.count()
        
        return JsonResponse({
            'status': 'success',
            'database_connected': True,
            'subject_count': count,
            'message': 'Database working correctly'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

def home(request):
    """Home page view"""
    try:
        # Get data for home page
        subjects_count = Subject.objects.count()
        
        if subjects_count == 0:
            # Tables exist but no data - show message
            context = {
                'no_data': True,
                'featured_articles': [],
                'featured_tests': [],
                'subjects': [],
            }
            return render(request, 'main/home.html', context)
        
        # Get data for home page
        featured_articles = Article.objects.select_related('topic__subject', 'author').filter(is_published=True)[:6]
        subjects = Subject.objects.all()[:6]
        
        # Try to get featured tests - handle if tests app isn't working
        try:
            featured_tests = MockTest.objects.filter(is_featured=True, is_active=True)[:4]
        except:
            featured_tests = []
        
        context = {
            'featured_articles': featured_articles,
            'featured_tests': featured_tests,
            'subjects': subjects,
            'no_data': False,
        }
        return render(request, 'main/home.html', context)
        
    except Exception as e:
        # If any error, show basic page with error info
        context = {
            'error': str(e),
            'featured_articles': [],
            'featured_tests': [],
            'subjects': [],
            'no_data': True,
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

def article_list(request):
    query = request.GET.get('q')
    subject_id = request.GET.get('subject')
    
    articles = Article.objects.filter(is_published=True).select_related('topic__subject', 'author')
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(topic__name__icontains=query) |
            Q(topic__subject__name__icontains=query)
        )
    
    if subject_id:
        articles = articles.filter(topic__subject_id=subject_id)
    
    subjects = Subject.objects.all()
    
    context = {
        'articles': articles,
        'subjects': subjects,
        'current_query': query,
        'current_subject': subject_id,
    }
    return render(request, 'main/article_list.html', context)

def article_search(request):
    """AJAX endpoint for article search"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'articles': []})
    
    articles = Article.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        is_published=True
    ).select_related('topic__subject', 'author')[:10]
    
    results = []
    for article in articles:
        results.append({
            'id': article.id,
            'title': article.title,
            'url': article.get_absolute_url(),
            'subject': article.topic.subject.name,
            'topic': article.topic.name,
        })
    
    return JsonResponse({'articles': results})

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleCreateForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully!')
            return redirect('main:article_detail', slug=article.slug)
    else:
        form = ArticleCreateForm()
    
    return render(request, 'main/article_create.html', {'form': form})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Check if user has bookmarked this article
    is_bookmarked = False
    user_note = None
    
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, article=article).exists()
        try:
            user_note = Note.objects.get(user=request.user, article=article)
        except Note.DoesNotExist:
            pass
    
    # Get related articles
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

def subject_list(request):
    subjects = Subject.objects.all().annotate(
        article_count=Count('topic__article', filter=Q(topic__article__is_published=True))
    )
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'main/subject_list.html', context)

def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    topics = subject.topic_set.all().annotate(
        article_count=Count('article', filter=Q(article__is_published=True))
    )
    
    context = {
        'subject': subject,
        'topics': topics,
    }
    return render(request, 'main/subject_detail.html', context)

@login_required
@require_POST
def toggle_bookmark(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, article=article)
    
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def bookmarks_api(request):
    """API endpoint to get user's bookmarks"""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('article__topic__subject')
    
    bookmark_data = []
    for bookmark in bookmarks:
        bookmark_data.append({
            'id': bookmark.article.id,
            'title': bookmark.article.title,
            'url': bookmark.article.get_absolute_url(),
            'subject': bookmark.article.topic.subject.name,
            'topic': bookmark.article.topic.name,
            'created_at': bookmark.created_at.isoformat(),
        })
    
    return JsonResponse({'bookmarks': bookmark_data})

@login_required
@require_POST
def save_note(request):
    article_id = request.POST.get('article_id')
    note_content = request.POST.get('note_content', '')
    
    article = get_object_or_404(Article, id=article_id)
    
    if note_content.strip():
        note, created = Note.objects.get_or_create(
            user=request.user,
            article=article,
            defaults={'content': note_content}
        )
        if not created:
            note.content = note_content
            note.save()
        
        return JsonResponse({'success': True, 'message': 'Note saved successfully!'})
    else:
        # Delete note if content is empty
        Note.objects.filter(user=request.user, article=article).delete()
        return JsonResponse({'success': True, 'message': 'Note deleted!'})

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