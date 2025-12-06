from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django import forms
import datetime
from core.models import Clazz, Teacher, Student, Staff, Enrollment, ClassType, Schedule, Attendance
from .forms import ClassForm, TeacherForm, StudentForm, StaffForm, EnrollmentForm, ClassTypeForm, ScheduleForm, AttendanceForm
from django.db.models import Count, Q

def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def admin_dashboard_view(request):
    query = request.GET.get('q')
    classes = Clazz.objects.annotate(
        enrolled_students=Count('enrollments')
    )

    if query:
        classes = classes.filter(
            Q(class_name__icontains=query) |
            Q(teacher__full_name__icontains=query)
        )

    # Calculate stats
    total_classes = Clazz.objects.count()
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    pending_requests_count = Enrollment.objects.filter(status='pending').count()

    context = {
        'classes': classes,
        'query': query,
        'total_classes': total_classes,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'pending_requests_count': pending_requests_count,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def admin_documents_view(request):
    # Placeholder for documents logic. 
    # In a real app, this would query a Document model.
    documents = [
        {'title': 'School Policy 2025', 'type': 'PDF', 'date': '2025-01-15'},
        {'title': 'Academic Calendar', 'type': 'PDF', 'date': '2025-01-20'},
        {'title': 'Teacher Handbook', 'type': 'DOCX', 'date': '2024-12-10'},
        {'title': 'Student Code of Conduct', 'type': 'PDF', 'date': '2024-09-01'},
    ]
    return render(request, 'dashboard/documents.html', {'documents': documents})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def admin_statistics_view(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_classes = Clazz.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    # Get enrollment growth (last 6 months) - simplified for demo
    # In a real app, use TruncMonth and proper aggregation
    recent_enrollments = Enrollment.objects.order_by('-enrollment_date')[:5]
    
    # Class distribution by type
    class_distribution = Clazz.objects.values('class_type__code').annotate(count=Count('class_id'))
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_enrollments': total_enrollments,
        'recent_enrollments': recent_enrollments,
        'class_distribution': class_distribution,
    }
    return render(request, 'dashboard/statistics.html', context)

@login_required
def student_dashboard_view(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect('home')
        
    enrollments = student.enrollments.all()
    return render(request, 'dashboard/student_dashboard.html', {
        'student': student,
        'enrollments': enrollments
    })

@login_required
def student_courses_view(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect('home')
    enrollments = student.enrollments.all().select_related('clazz', 'clazz__class_type', 'clazz__teacher')
    return render(request, 'dashboard/student_courses.html', {'student': student, 'enrollments': enrollments})

@login_required
def student_schedule_view(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect('home')
    
    # Get all enrollments for the student
    enrollments = student.enrollments.all()
    
    # Get all schedules related to the student's enrolled classes
    schedules = Schedule.objects.filter(clazz__enrollments__student=student).distinct()

    return render(request, 'dashboard/student_schedule.html', {'student': student, 'schedules': schedules})

@login_required
def student_pending_requests_view(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect('home')
    
    pending_enrollments = student.enrollments.filter(status='pending')
    return render(request, 'dashboard/student_pending.html', {'student': student, 'enrollments': pending_enrollments})

@login_required
def student_achievements_view(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect('home')
    
    enrollments = student.enrollments.all().select_related('clazz', 'clazz__class_type', 'clazz__teacher')

    return render(request, 'dashboard/student_achievements.html', {'student': student, 'enrollments': enrollments})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def add_class_view(request):
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Class added successfully!")
            return redirect('dashboard:dashboard')
    else:
        form = ClassForm()
    return render(request, 'dashboard/add_class.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def edit_class_view(request, pk):
    clazz = get_object_or_404(Clazz, pk=pk)
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES, instance=clazz)
        if form.is_valid():
            form.save()
            messages.success(request, "Class updated successfully!")
            return redirect('dashboard:dashboard')
    else:
        form = ClassForm(instance=clazz)
    return render(request, 'dashboard/edit_class.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def delete_class_view(request, pk):
    clazz = get_object_or_404(Clazz, pk=pk)
    clazz.delete()
    messages.success(request, "Class deleted successfully!")
    return redirect('dashboard:dashboard')

# Student Management
@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_students_view(request):
    query = request.GET.get('q')
    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, 'dashboard/manage_students.html', {'students': students, 'query': query})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def add_student_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully!")
            return redirect('dashboard:manage_students')
    else:
        form = StudentForm()
    return render(request, 'dashboard/add_student.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def edit_student_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect('dashboard:manage_students')
    else:
        form = StudentForm(instance=student)
    return render(request, 'dashboard/edit_student.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def delete_student_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect('dashboard:manage_students')

# Teacher Management
@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_teachers_view(request):
    query = request.GET.get('q')
    teachers = Teacher.objects.all()

    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, 'dashboard/manage_teachers.html', {'teachers': teachers, 'query': query})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def add_teacher_view(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher added successfully!")
            return redirect('dashboard:manage_teachers')
    else:
        form = TeacherForm()
    return render(request, 'dashboard/add_teacher.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def edit_teacher_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher updated successfully!")
            return redirect('dashboard:manage_teachers')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'dashboard/edit_teacher.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def delete_teacher_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.delete()
    messages.success(request, "Teacher deleted successfully!")
    return redirect('dashboard:manage_teachers')

# Enrollment Management
@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_enrollments_view(request):
    query = request.GET.get('q')
    
    # Base querysets
    active_enrollments = Enrollment.objects.filter(status='approved').select_related('student', 'clazz')
    pending_requests = Enrollment.objects.filter(status='pending').select_related('student', 'clazz')

    if query:
        # Apply search to both
        search_filter = Q(student__full_name__icontains=query) | Q(clazz__class_name__icontains=query)
        active_enrollments = active_enrollments.filter(search_filter)
        pending_requests = pending_requests.filter(search_filter)

    return render(request, 'dashboard/manage_enrollments.html', {
        'active_enrollments': active_enrollments, 
        'pending_requests': pending_requests,
        'query': query
    })

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_requests_view(request):
    requests = Enrollment.objects.filter(status='pending').select_related('student', 'clazz')
    return render(request, 'dashboard/manage_requests.html', {'requests': requests})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def approve_request_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.status = 'approved'
    enrollment.is_paid = True # Auto-mark as paid upon approval
    enrollment.save()
    messages.success(request, f"Enrollment for {enrollment.student.full_name} approved and payment verified.")
    return redirect('dashboard:manage_enrollments')

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def reject_request_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.status = 'rejected'
    enrollment.save()
    messages.warning(request, f"Enrollment for {enrollment.student.full_name} rejected.")
    return redirect('dashboard:manage_enrollments')

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def add_enrollment_view(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student enrolled successfully!")
            return redirect('dashboard:manage_enrollments')
    else:
        form = EnrollmentForm()
    return render(request, 'dashboard/add_enrollment.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def delete_enrollment_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.delete()
    messages.success(request, "Enrollment removed successfully!")
    return redirect('dashboard:manage_enrollments')

# Staff Management
@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_staff_view(request):
    query = request.GET.get('q')
    staff_members = Staff.objects.all()

    if query:
        staff_members = staff_members.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(position__icontains=query)
        )

    return render(request, 'dashboard/manage_staff.html', {'staff_members': staff_members, 'query': query})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def add_staff_view(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member added successfully!")
            return redirect('dashboard:manage_staff')
    else:
        form = StaffForm()
    return render(request, 'dashboard/add_staff.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def edit_staff_view(request, pk):
    staff_member = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member updated successfully!")
            return redirect('dashboard:manage_staff')
    else:
        form = StaffForm(instance=staff_member)
    return render(request, 'dashboard/edit_staff.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def delete_staff_view(request, pk):
    staff_member = get_object_or_404(Staff, pk=pk)
    staff_member.delete()
    messages.success(request, "Staff member deleted successfully!")
    return redirect('dashboard:manage_staff')

# Class Type Management
@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_class_types_view(request):
    class_types = ClassType.objects.all()
    return render(request, 'dashboard/manage_class_types.html', {'class_types': class_types})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def add_class_type_view(request):
    if request.method == 'POST':
        form = ClassTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class Type added successfully!")
            return redirect('dashboard:manage_class_types')
    else:
        form = ClassTypeForm()
    return render(request, 'dashboard/add_class_type.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def edit_class_type_view(request, pk):
    class_type = get_object_or_404(ClassType, pk=pk)
    if request.method == 'POST':
        form = ClassTypeForm(request.POST, instance=class_type)
        if form.is_valid():
            form.save()
            messages.success(request, "Class Type updated successfully!")
            return redirect('dashboard:manage_class_types')
    else:
        form = ClassTypeForm(instance=class_type)
    return render(request, 'dashboard/edit_class_type.html', {'form': form})

@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def delete_class_type_view(request, pk):
    class_type = get_object_or_404(ClassType, pk=pk)
    class_type.delete()
    messages.success(request, "Class Type deleted successfully!")
    return redirect('dashboard:manage_class_types')

# Schedule Management
@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_schedule_view(request, class_pk):
    clazz = get_object_or_404(Clazz, pk=class_pk)
    try:
        schedule = clazz.schedule
    except Schedule.DoesNotExist:
        schedule = None

    if request.method == 'POST':
        if schedule:
            form = ScheduleForm(request.POST, instance=schedule)
        else:
            form = ScheduleForm(request.POST)
        
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.clazz = clazz
            schedule.save()
            messages.success(request, "Schedule updated successfully!")
            return redirect('dashboard:dashboard') # Redirect to dashboard or class list
    else:
        if schedule:
            form = ScheduleForm(instance=schedule)
        else:
            form = ScheduleForm(initial={'clazz': clazz})
            # Hide clazz field since we are setting it automatically, or make it read-only
            form.fields['clazz'].widget = forms.HiddenInput()

    return render(request, 'dashboard/manage_schedule.html', {'form': form, 'clazz': clazz})

# Attendance Management
@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def take_attendance_view(request, class_pk):
    clazz = get_object_or_404(Clazz, pk=class_pk)
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
             date = datetime.date.today()
    else:
        date = datetime.date.today()
        
    enrollments = clazz.enrollments.all().select_related('student')
    
    if request.method == 'POST':
        date_str_post = request.POST.get('date')
        if date_str_post:
             date = datetime.datetime.strptime(date_str_post, '%Y-%m-%d').date()

        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.pk}')
            if status:
                Attendance.objects.update_or_create(
                    enrollment=enrollment,
                    date=date,
                    defaults={'status': status}
                )
        messages.success(request, f"Attendance recorded for {date}")
        return redirect(f"{request.path}?date={date}")

    # Prepare data for template
    attendance_data = []
    for enrollment in enrollments:
        attendance = Attendance.objects.filter(enrollment=enrollment, date=date).first()
        attendance_data.append({
            'enrollment': enrollment,
            'status': attendance.status if attendance else None
        })
        
    return render(request, 'dashboard/take_attendance.html', {
        'clazz': clazz,
        'date': date,
        'attendance_data': attendance_data
    })