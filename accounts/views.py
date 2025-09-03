from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from .forms import LoginForm
import os
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm, UserUpdateForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Save basic user first
            user.save()
            # Create profile with selected role
            role = form.cleaned_data.get('role')
            admin_code = form.cleaned_data.get('admin_code')

            # If the user selected 'admin', ensure correct admin_code
            if role == 'admin':
                if not admin_code or admin_code != os.environ.get('SITE_ADMIN_CODE'):
                    # remove created user and show error
                    user.delete()
                    messages.error(request, 'Invalid admin code provided for admin registration.')
                    return redirect('accounts:register')
                else:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()

            UserProfile.objects.get_or_create(user=user, defaults={'role': role})

            login(request, user)
            messages.success(request, 'Registration successful! Welcome to GATE Mining Prep!')
            return redirect('main:dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Replacement for the default LoginView that accepts a role selector
    and records the user's actual role in the session for UI convenience.
    """
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        # Standard login
        # Before finalizing login, validate optional role selector against stored role
        selected_role = form.cleaned_data.get('role')
        user = form.get_user()

        # Determine authoritative role: prefer userprofile.role, fallback to staff
        try:
            actual_role = user.userprofile.role
        except Exception:
            actual_role = 'admin' if user.is_staff else None

        # If a role was selected in the form, ensure it matches the authoritative role
        if selected_role:
            # allow admin to be recognized via is_staff
            if selected_role == 'admin' and user.is_staff:
                pass
            elif actual_role and selected_role != actual_role:
                messages.error(self.request, 'Selected role does not match your account role.')
                return self.form_invalid(form)

        # Proceed with normal login
        response = super().form_valid(form)

        if actual_role:
            self.request.session['role'] = actual_role

        return response

@login_required
def profile(request):
    user_profile = request.user.userprofile
    recent_tests = request.user.testattempt_set.filter(is_completed=True)[:5]
    bookmarks = request.user.bookmark_set.all()[:5]
    
    context = {
        'user_profile': user_profile,
        'recent_tests': recent_tests,
        'bookmarks': bookmarks,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.userprofile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/edit_profile.html', context)