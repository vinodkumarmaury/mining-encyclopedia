from django.db import models
from django.contrib.auth.models import User
from main.models import Subject, Topic
import json

class MockTest(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='mock_tests')
    topics = models.ManyToManyField(Topic, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    duration_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()

class Question(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('numerical', 'Numerical'),
        ('true_false', 'True/False'),
    ]
    
    mock_test = models.ForeignKey(MockTest, on_delete=models.CASCADE, related_name='questions')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    options = models.JSONField(default=dict, blank=True)  # For MCQ options
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    marks = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=10, choices=MockTest.DIFFICULTY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q{self.id} - {self.mock_test.title}"

class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mock_test = models.ForeignKey(MockTest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    time_taken_minutes = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.mock_test.title}"

class Answer(models.Model):
    test_attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.FloatField(default=0)
    time_taken_seconds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.test_attempt.user.username} - Q{self.question.id}"

class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_score = models.FloatField(default=0)
    tests_completed = models.PositiveIntegerField(default=0)
    average_percentage = models.FloatField(default=0)
    rank = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"{self.user.username} - Rank {self.rank}"