from django import forms
from .models import Article, Topic

class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'excerpt', 'content', 'topic', 'difficulty', 'featured_image', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
