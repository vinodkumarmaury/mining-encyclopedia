from django.contrib import admin
from .models import Subject, Topic, Article, Bookmark, Note

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('name', 'subject__name')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty', 'is_published', 'views', 'created_at')
    list_filter = ('difficulty', 'is_published', 'topic__subject')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')