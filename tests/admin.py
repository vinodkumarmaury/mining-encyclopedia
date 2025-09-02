from django.contrib import admin
from .models import MockTest, Question, TestAttempt, Answer, Leaderboard

@admin.register(MockTest)
class MockTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'difficulty', 'duration_minutes', 'total_marks', 'is_active')
    list_filter = ('subject', 'difficulty', 'is_active')
    search_fields = ('title', 'description')
    filter_horizontal = ('topics',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'mock_test', 'topic', 'question_type', 'difficulty', 'marks')
    list_filter = ('question_type', 'difficulty', 'topic__subject')
    search_fields = ('question_text',)

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'mock_test', 'percentage', 'is_completed', 'started_at')
    list_filter = ('is_completed', 'mock_test__subject')
    readonly_fields = ('started_at', 'completed_at')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('test_attempt', 'question', 'is_correct', 'marks_obtained')
    list_filter = ('is_correct',)

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'total_score', 'tests_completed', 'average_percentage')
    ordering = ('rank',)
    readonly_fields = ('updated_at',)