from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.db import transaction
from .forms import SimpleSignUpForm
from core.models import Teacher, Student


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:admin_dashboard')

        is_teacher = hasattr(request.user, 'teacher_profile')
        if is_teacher:
            return redirect('dashboard:teacher_dashboard')
        else:
            return redirect('dashboard:student_dashboard')

    next_url = request.GET.get('next')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            redirect_to = request.POST.get('next') or next_url
            if redirect_to and url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(redirect_to)

            if user.is_staff:
                return redirect('dashboard:admin_dashboard')

            is_teacher = hasattr(user, 'teacher_profile')
            if is_teacher:
                return redirect('dashboard:teacher_dashboard')
            else:
                return redirect('dashboard:student_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect('home')


def signup_view(request):
    if request.method == 'POST':
        form = SimpleSignUpForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    role = form.cleaned_data.get('role', 'student')

                    common_data = {
                        'user': user,
                        'full_name': form.cleaned_data['full_name'],
                        'dob': form.cleaned_data['dob'],
                        'phone_number': form.cleaned_data['phone_number'],
                        'email': form.cleaned_data['email'],
                        'address': form.cleaned_data['address']
                    }

                    if role == 'teacher':
                        Teacher.objects.create(
                            **common_data,
                            qualification=form.cleaned_data.get(
                                'qualification', '')
                        )
                    else:
                        Student.objects.create(**common_data)

                    login(request, user)
                    messages.success(request, "Account created successfully!")
                    if role == 'teacher':
                        return redirect('dashboard:teacher_dashboard')
                    else:
                        return redirect('dashboard:student_dashboard')
            except Exception as e:
                print(f"Signup Error: {e}")
                messages.error(
                    request, "An error occurred during signup. Please ensure your information is correct and try again.")
    else:
        form = SimpleSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
