from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'college', 'graduation_year', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'college': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
    ('professor', 'Professor'),
    ('admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm p-2'}))
    admin_code = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm p-2'}),
                                 help_text='Optional admin code (leave blank for normal users)')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'admin_code']


class LoginForm(AuthenticationForm):
    """Custom login form with optional role selector.

    The role selector is primarily UI convenience; the server will validate
    that the selected role matches the user's stored profile role and will
    store the actual role in the session.
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
    ('professor', 'Professor'),
    ('admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure consistent bootstrap classes for username/password widgets
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({'class': 'block w-full rounded-md border-gray-300 shadow-sm p-2'})
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({'class': 'block w-full rounded-md border-gray-300 shadow-sm p-2'})