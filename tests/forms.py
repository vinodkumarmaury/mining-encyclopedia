from django import forms
from .models import MockTest

class MockTestCreateForm(forms.ModelForm):
    class Meta:
        model = MockTest
        fields = ['title', 'description', 'subject', 'topics', 'difficulty', 'duration_minutes', 'total_marks', 'is_active', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'rows':3}),
            'subject': forms.Select(attrs={'class':'form-control'}),
            'topics': forms.SelectMultiple(attrs={'class':'form-control'}),
            'difficulty': forms.Select(attrs={'class':'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks': forms.NumberInput(attrs={'class':'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
