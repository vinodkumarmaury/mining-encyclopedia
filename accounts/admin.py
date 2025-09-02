from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'graduation_year', 'total_tests_taken', 'streak_days', 'is_premium')
    list_filter = ('is_premium', 'graduation_year')
    search_fields = ('user__username', 'user__email', 'college')
    readonly_fields = ('total_tests_taken', 'total_articles_read', 'created_at')