from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Clazz, Student, Teacher, Enrollment
from django.db.models import Q


def get_display_name(user):
    """
    Returns the full name of the user based on their role profile,
    or their username if no profile is found.
    """
    if not user.is_authenticated:
        return ""

    try:
        if hasattr(user, 'teacher_profile'):
            return user.teacher_profile.full_name
        if hasattr(user, 'student_profile'):
            return user.student_profile.full_name
        if hasattr(user, 'admin_profile'):
            return user.admin_profile.full_name
    except Exception:
        pass

    return user.username


def home(request):
    """Renders the home page with featured classes."""
    featured_classes = Clazz.objects.all().order_by('-class_id')[:3]
    context = {
        'classes': featured_classes,
        'user_display_name': get_display_name(request.user)
    }
    return render(request, 'core/home.html', context)


def class_list(request):
    """Fetches and displays all available classes with search functionality."""
    all_classes = Clazz.objects.all().order_by('class_name')
    query = request.GET.get('q')
    if query:
        all_classes = all_classes.filter(
            Q(class_name__icontains=query) |
            Q(class_type__description__icontains=query) |
            Q(class_type__code__icontains=query) |
            Q(teacher__full_name__icontains=query)
        )
    context = {
        'classes': all_classes,
        'query': query,
        'user_display_name': get_display_name(request.user)
    }
    return render(request, 'core/class_list.html', context)


def class_detail(request, pk):
    """Displays detailed information for a single class."""
    clazz = get_object_or_404(Clazz, pk=pk)
    context = {
        'clazz': clazz,
        'enrollments': clazz.enrollments.all(),
        'user_display_name': get_display_name(request.user)
    }
    return render(request, 'core/class_detail.html', context)


@login_required
def enroll_student(request, class_id):
    clazz = get_object_or_404(Clazz, pk=class_id)

    # Check if user has a student profile
    try:
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        messages.error(request, "Only students can enroll in classes.")
        return redirect('class_detail', pk=class_id)

    # Check if already enrolled (or requested)
    enrollment = Enrollment.objects.filter(
        student=student, clazz=clazz).first()
    if enrollment:
        if enrollment.status == 'approved':
            messages.warning(
                request, "You are already enrolled in this class.")
            return redirect('dashboard:student_dashboard')
        elif enrollment.status == 'pending':
            messages.info(
                request, "You have already requested to enroll in this class. Please wait for approval.")
            return redirect('dashboard:student_dashboard')
        elif enrollment.status == 'rejected':
            messages.error(
                request, "Your previous enrollment request for this class was rejected.")
        return redirect('class_detail', pk=class_id)

    # Create enrollment request
    Enrollment.objects.create(student=student, clazz=clazz, status='pending')
    messages.success(
        request, f"Enrollment request for {clazz.class_name} sent successfully! Please wait for admin approval.")
    return redirect('dashboard:student_dashboard')


def features(request):
    """Renders the features page."""
    return render(request, 'core/features.html')
