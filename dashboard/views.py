from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django import forms
import datetime
import calendar
import random
from django.urls import reverse
import uuid
from core.models import (
    Clazz, Admin, Teacher, Student, Enrollment, ClassType, Attendance,
    Material, Announcement, Assignment, AssignmentSubmission, Feedback, Message,
    AttendanceSession, ContentReadStatus
)
from .forms import ClassForm, TeacherForm, StudentForm, StaffForm, EnrollmentForm, ClassTypeForm, ScheduleForm, AttendanceForm, MaterialForm, AnnouncementForm, AssignmentForm, AssignmentSubmissionForm, AssignmentGradingForm, AssignmentCreateForm, FeedbackForm, MessageForm
from django.db.models import Count, Q, Avg


@login_required
def teacher_create_assignment_view(request):
    try:
        teacher = request.user.teacher_profile
    except (AttributeError, Teacher.DoesNotExist):
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')

    if request.method == 'POST':
        form = AssignmentCreateForm(request.POST, teacher=teacher)

        if form.is_valid():
            form.save()
            messages.success(request, "Assignment created successfully!")
            return redirect('dashboard:teacher_assignments')
    else:
        form = AssignmentCreateForm(teacher=teacher)

    return render(request, 'dashboard/teacher_create_assignment.html', {'form': form})


@login_required
def teacher_feedback_list_view(request):
    try:
        teacher = request.user.teacher_profile
    except (AttributeError, Teacher.DoesNotExist):
        return redirect('home')

    feedbacks = Feedback.objects.filter(
        clazz__teacher=teacher).select_related('clazz').order_by('-created_at')
    avg_teacher = feedbacks.aggregate(Avg('teacher_rate'))['teacher_rate__avg']
    avg_class = feedbacks.aggregate(Avg('class_rate'))['class_rate__avg']

    return render(request, 'dashboard/teacher_feedback_list.html', {
        'feedbacks': feedbacks,
        'avg_teacher': round(avg_teacher, 1) if avg_teacher else 0,
        'avg_class': round(avg_class, 1) if avg_class else 0,
    })


@login_required
def student_give_feedback_view(request, class_pk):
    try:
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        return redirect('home')

    clazz = get_object_or_404(Clazz, pk=class_pk)
    if not Enrollment.objects.filter(student=student, clazz=clazz, status='approved').exists():
        messages.error(request, "You are not enrolled in this class.")
        return redirect('dashboard:student_courses')

    if Feedback.objects.filter(student=student, clazz=clazz).exists():
        messages.info(
            request, "You have already submitted feedback for this class.")
        return redirect('dashboard:student_class_detail', class_pk=class_pk)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = student
            feedback.clazz = clazz
            feedback.teacher = clazz.teacher
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect('dashboard:student_class_detail', class_pk=class_pk)
    else:
        form = FeedbackForm()

    return render(request, 'dashboard/student_give_feedback.html', {'form': form, 'clazz': clazz})


def get_display_name(user):
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


@login_required
def messages_view(request):
    user = request.user
    from django.contrib.auth.models import User

    contacts_map = {}

    def get_or_create_contact(u):
        if u.pk not in contacts_map:
            u.class_names = set()
            u.role_label = "User"  # Default
            contacts_map[u.pk] = u
        return contacts_map[u.pk]

    is_student = hasattr(user, 'student_profile')
    is_teacher = hasattr(user, 'teacher_profile')

    if is_student:
        student = user.student_profile
        enrollments = Enrollment.objects.filter(student=student, status='approved').select_related(
            'clazz', 'clazz__teacher', 'clazz__teacher__user')

        for enrollment in enrollments:
            clazz = enrollment.clazz
            c_name = clazz.class_name
            if clazz.teacher and clazz.teacher.user:
                t_user = clazz.teacher.user
                contact = get_or_create_contact(t_user)
                contact.role_label = "Teacher"
                contact.class_names.add(c_name)

            classmates = Student.objects.filter(enrollments__clazz=clazz, enrollments__status='approved').exclude(
                pk=student.pk).select_related('user')
            for cm in classmates:
                if cm.user:
                    contact = get_or_create_contact(cm.user)
                    contact.role_label = "Student"
                    contact.class_names.add(c_name)
    elif is_teacher:
        teacher = user.teacher_profile
        classes = Clazz.objects.filter(teacher=teacher)

        for clazz in classes:
            c_name = clazz.class_name
            students = Student.objects.filter(
                enrollments__clazz=clazz, enrollments__status='approved').select_related('user')
            for s in students:
                if s.user:
                    contact = get_or_create_contact(s.user)
                    contact.role_label = "Student"
                    contact.class_names.add(c_name)

    # --- 2. Populate from Message History ---
    received_ids = Message.objects.filter(
        recipient=user).values_list('sender_id', flat=True)
    sent_ids = Message.objects.filter(
        sender=user).values_list('recipient_id', flat=True)
    history_ids = set(received_ids) | set(sent_ids)

    history_users = User.objects.filter(id__in=history_ids)
    for h_user in history_users:
        if h_user.pk not in contacts_map:
            contact = get_or_create_contact(h_user)
            # Try to infer role
            if hasattr(h_user, 'teacher_profile'):
                contact.role_label = "Teacher"
            elif hasattr(h_user, 'student_profile'):
                contact.role_label = "Student"
            elif hasattr(h_user, 'admin_profile'):
                contact.role_label = "Admin"
            # No class names for pure history contacts (unless we want to fetch them, but spec implies showing "class" for class relations)

    # --- 3. Search Functionality ---
    search_query = request.GET.get('search_user')
    search_role = request.GET.get('search_role')

    # If searching, we might need to fetch users NOT in contacts_map yet
    if search_query or search_role:
        search_results = User.objects.exclude(pk=user.pk)

        if search_query:
            # We need to filter based on related models, but not all users have all related models.
            # We can use Q objects to check for existence AND match.
            # However, simpler approach: Filter by username OR (student__full_name) OR (teacher__full_name) OR (staff__full_name)
            # The error "Cannot resolve keyword 'staff'" implies 'staff' related name might be missing or different.
            # Checking models.py: Staff model does not have 'user' field linked! It inherits from Person but no OneToOne to User.
            # Wait, let's re-read models.py.
            # Teacher has user = OneToOneField. Student has user = OneToOneField.
            # Staff has NO user field in the provided models.py content!
            # Ah, looking at models.py again:
            # class Staff(Person): ... no user field.
            # But earlier code used user.staff.
            # If Staff doesn't have a user field, we can't search Users by Staff fields directly via ORM if they aren't linked.
            # Let's assume for now we only search Student and Teacher if Staff is not linked.
            # OR, maybe I missed it. Let's check if 'staff' is actually a related name on User.
            # Django User model doesn't have 'staff' unless we added it or a OneToOne defined it.
            # The error confirms 'staff' is not a field on User.

            # SAFE SEARCH: Filter by username first.
            # Then optionally filter by student/teacher if they exist.

            query_filter = Q(username__icontains=search_query)

            # Check if 'student' relation exists (it should based on models)
            query_filter |= Q(student__full_name__icontains=search_query)

            # Check if 'teacher' relation exists
            query_filter |= Q(teacher__full_name__icontains=search_query)

            # For Staff, since the model shows no user link, we can't search User via staff__full_name.
            # Unless there's a different relation or I missed something.
            # I will exclude staff search for now to fix the crash, or just search by username.
            # If user.is_staff is used for "Staff" role, we can search by username for them.

            search_results = search_results.filter(query_filter)

        if search_role:
            if search_role == 'student':
                search_results = search_results.filter(student__isnull=False)
            elif search_role == 'teacher':
                search_results = search_results.filter(teacher__isnull=False)
            elif search_role == 'staff':
                search_results = search_results.filter(is_staff=True)

        # Limit results
        search_results = search_results.distinct()[:50]

        # Re-build contacts list based on search results?
        # Or just filter the existing map AND add new search hits?
        # The prompt implies "left sidebar will ... show all ... to choose".
        # Usually search *filters* the list. But if I search for someone new (e.g. admin), they should appear.

        # Strategy: Clear map if search is active? Or Filter?
        # Let's create a new list for search results, enriching them from the map if they exist there.
        final_contacts = []
        for res in search_results:
            if res.pk in contacts_map:
                final_contacts.append(contacts_map[res.pk])
            else:
                # New find
                res.class_names = set()
                # Infer role
                if hasattr(res, 'teacher_profile'):
                    res.role_label = "Teacher"
                elif hasattr(res, 'student_profile'):
                    res.role_label = "Student"
                elif res.is_staff:
                    res.role_label = "Admin"
                else:
                    res.role_label = "User"
                final_contacts.append(res)
        contacts = final_contacts

    else:
        # No search: Show all collected contacts
        contacts = list(contacts_map.values())

    # --- 4. Handle Specific Chat Selection ---
    chat_username = request.GET.get('chat_with')
    active_contact = None
    messages_list = []

    if chat_username:
        active_contact = get_object_or_404(User, username=chat_username)
        messages_list = Message.objects.filter(
            Q(sender=user, recipient=active_contact) |
            Q(sender=active_contact, recipient=user)
        ).order_by('created_at')

        # Mark as read
        Message.objects.filter(
            recipient=user, sender=active_contact, is_read=False).update(is_read=True)

        # Ensure active contact is in the list
        found = False
        for c in contacts:
            if c.pk == active_contact.pk:
                found = True
                break
        if not found:
            # Add active contact to top
            if active_contact.pk in contacts_map:
                contacts.insert(0, contacts_map[active_contact.pk])
            else:
                active_contact.class_names = set()
                if hasattr(active_contact, 'teacher_profile'):
                    active_contact.role_label = "Teacher"
                elif hasattr(active_contact, 'student_profile'):
                    active_contact.role_label = "Student"
                elif hasattr(active_contact, 'admin_profile'):
                    active_contact.role_label = "Admin"
                else:
                    active_contact.role_label = "User"
                contacts.insert(0, active_contact)

    # --- 5. Final Formatting & Sorting for Display ---
    for contact in contacts:
        contact.display_name = get_display_name(contact)

        # Format Class Label
        if hasattr(contact, 'class_names') and contact.class_names:
            # Sort for consistency
            sorted_classes = sorted(list(contact.class_names))
            if len(sorted_classes) > 2:
                contact.class_label = f"{', '.join(sorted_classes[:2])} +{len(sorted_classes)-2}"
            else:
                contact.class_label = ", ".join(sorted_classes)
        else:
            contact.class_label = ""

        # Fallback subtitle
        if contact.class_label:
            contact.display_subtitle = f"{contact.role_label} • {contact.class_label}"
        else:
            contact.display_subtitle = f"{contact.role_label} • {contact.username}"

        # Get Last Message & Unread Status
        last_msg = Message.objects.filter(
            Q(sender=user, recipient=contact) |
            Q(sender=contact, recipient=user)
        ).order_by('-created_at').first()

        contact.last_message_time = last_msg.created_at if last_msg else None

        # Check for unread messages FROM this contact
        contact.has_unread = Message.objects.filter(
            sender=contact,
            recipient=user,
            is_read=False
        ).exists()

    # Sort contacts: Unread first, then by Last Message Time (newest first)
    # We use a tuple for sort key: (has_unread (True > False), last_message_time (Date > None))
    # Python sorts False < True, so reverse=True puts True first.
    # For datetime, newer is "greater", so reverse=True puts newer first.
    # We need to handle None for last_message_time safely.

    def contact_sort_key(c):
        # 1. Has Unread (1 if True, 0 if False)
        k1 = 1 if getattr(c, 'has_unread', False) else 0

        # 2. Last Message Time (timestamp)
        # Use a very old date for None so they drop to bottom
        k2 = getattr(c, 'last_message_time', datetime.datetime.min)
        if k2 is None:  # explicit check if getattr returned None somehow or if value is None
            k2 = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

        return (k1, k2)

    contacts.sort(key=contact_sort_key, reverse=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = user
            msg.recipient = form.cleaned_data['recipient_username']
            msg.save()
            messages.success(request, "Message sent!")
            # Redirect back to the same chat
            return redirect(f"{request.path}?chat_with={msg.recipient.username}")
    else:
        # Pre-fill recipient if chatting
        initial = {
            'recipient_username': active_contact.username} if active_contact else {}
        form = MessageForm(initial=initial)

    # Determine base template and context
    context = {
        'contacts': contacts,
        'active_contact': active_contact,
        'messages_list': messages_list,
        'form': form,
    }

    if is_teacher:
        base_template = 'dashboard/teacher_base_dashboard.html'
        context['teacher'] = user.teacher_profile
    elif is_student:
        base_template = 'dashboard/student_base_dashboard.html'
        context['student'] = user.student_profile
    else:
        base_template = 'dashboard/base_dashboard.html'

    context['base_template'] = base_template

    return render(request, 'dashboard/messages.html', context)


def is_staff_user(user):
    # Check if user has admin profile OR is superuser
    if user.is_superuser:
        return True
    try:
        return hasattr(user, 'admin_profile')
    except:
        return False


def is_teacher_or_staff(user):
    if user.is_superuser:
        return True
    try:
        return hasattr(user, 'teacher_profile') or hasattr(user, 'admin_profile')
    except:
        return False


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

    # Get pending enrollments for the widget
    pending_enrollments = Enrollment.objects.filter(status='pending').select_related(
        'student', 'clazz').order_by('-enrollment_date')[:5]
    pending_requests_count = Enrollment.objects.filter(
        status='pending').count()

    context = {
        'classes': classes,
        'query': query,
        'total_classes': total_classes,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'pending_requests_count': pending_requests_count,
        'pending_enrollments': pending_enrollments,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def teacher_dashboard_view(request):
    try:
        teacher = request.user.teacher_profile
    except (AttributeError, Teacher.DoesNotExist):
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')

    today = datetime.date.today()

    # 1. Today's Schedule
    try:
        today_name_en = today.strftime('%A')
        day_mapping = {
            'Monday': 'Thứ 2',
            'Tuesday': 'Thứ 3',
            'Wednesday': 'Thứ 4',
            'Thursday': 'Thứ 5',
            'Friday': 'Thứ 6',
            'Saturday': 'Thứ 7',
            'Sunday': 'Chủ Nhật'
        }
        today_name_vn = day_mapping.get(today_name_en, today_name_en)

        today_schedule = Clazz.objects.filter(
            teacher=teacher,
            day_of_week__icontains=today_name_vn
        ).select_related('class_type').order_by('start_time')
    except Exception as e:
        today_schedule = []
        print(f"Error loading schedule: {e}")

    # 2. Working Statistics (Sessions based on Attendance records)
    try:
        monthly_sessions = Attendance.objects.filter(
            enrollment__clazz__teacher=teacher,
            date__month=today.month,
            date__year=today.year
        ).values('enrollment__clazz', 'date').distinct().count()

        yearly_sessions = Attendance.objects.filter(
            enrollment__clazz__teacher=teacher,
            date__year=today.year
        ).values('enrollment__clazz', 'date').distinct().count()
    except Exception as e:
        monthly_sessions = 0
        yearly_sessions = 0
        print(f"Error loading sessions: {e}")

    # 3. Class Data & Overall Stats
    classes = []
    total_attendance_rate = 0
    total_avg_grade = 0
    active_classes_count = 0
    overall_attendance = 0
    overall_grade = 0
    total_students = 0

    try:
        classes_qs = Clazz.objects.filter(teacher=teacher).annotate(
            student_count=Count('enrollments', filter=Q(
                enrollments__status='approved'))
        )

        for clazz in classes_qs:
            # Progress & Active Status
            if clazz.start_date and clazz.end_date:
                total_days = (clazz.end_date - clazz.start_date).days
                if total_days > 0:
                    days_elapsed = (today - clazz.start_date).days
                    progress = (days_elapsed / total_days) * 100
                    progress = max(0, min(100, progress))
                else:
                    progress = 100 if today >= clazz.end_date else 0

                clazz.is_active = clazz.start_date <= today <= clazz.end_date
            else:
                progress = 0
                clazz.is_active = False

            clazz.progress = int(progress)

            # Class Statistics
            # Attendance Rate
            total_presents = Attendance.objects.filter(
                enrollment__clazz=clazz, status='Present').count()
            total_records = Attendance.objects.filter(
                enrollment__clazz=clazz).count()
            if total_records > 0:
                clazz.attendance_rate = int(
                    (total_presents / total_records) * 100)
            else:
                clazz.attendance_rate = 0

            # Average Grade (Final Test)
            valid_grades = Enrollment.objects.filter(
                clazz=clazz, status='approved', final_test__isnull=False)
            avg_grade = valid_grades.aggregate(Avg('final_test'))[
                'final_test__avg']
            clazz.avg_grade = round(
                avg_grade, 1) if avg_grade is not None else "N/A"

            # Aggregate for Overall Stats (only if class has data)
            if total_records > 0:
                total_attendance_rate += clazz.attendance_rate
            if avg_grade is not None:
                total_avg_grade += avg_grade

            if clazz.student_count > 0:
                active_classes_count += 1

            classes.append(clazz)

        # Calculate Overall Averages
        overall_attendance = int(
            total_attendance_rate / len(classes)) if classes else 0
        overall_grade = round(
            total_avg_grade / active_classes_count, 1) if active_classes_count > 0 else 0

        # Total Students
        total_students = Student.objects.filter(
            enrollments__clazz__teacher=teacher,
            enrollments__status='approved'
        ).distinct().count()
    except Exception as e:
        print(f"Error loading class stats: {e}")

    return render(request, 'dashboard/teacher_dashboard.html', {
        'teacher': teacher,
        'classes': classes,
        'today_schedule': today_schedule,
        'monthly_sessions': monthly_sessions,
        'yearly_sessions': yearly_sessions,
        'overall_attendance': overall_attendance,
        'overall_grade': overall_grade,
        'total_students': total_students,
        'today': today,
    })


@login_required
def teacher_assignments_view(request):
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')

    teacher = request.user.teacher_profile
    assignments = Assignment.objects.filter(
        clazz__teacher=teacher).select_related('clazz').order_by('-due_date')

    return render(request, 'dashboard/teacher_assignments.html', {
        'assignments': assignments,
    })


@login_required
def teacher_statistics_view(request):
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')

    teacher = request.user.teacher_profile
    today = datetime.date.today()

    # 1. Detailed Class Stats
    classes_qs = Clazz.objects.filter(teacher=teacher).annotate(
        total_enrollments=Count('enrollments', filter=Q(
            enrollments__status='approved'))
    )

    class_stats = []
    students_at_risk = []

    total_classes = 0
    total_students_unique = set()
    global_attendance_sum = 0
    global_attendance_count = 0
    global_grade_sum = 0
    global_grade_count = 0

    for clazz in classes_qs:
        total_classes += 1

        # Attendance for this class
        total_sessions = Attendance.objects.filter(
            enrollment__clazz=clazz).count()
        total_presents = Attendance.objects.filter(
            enrollment__clazz=clazz, status='Present').count()

        attendance_rate = (total_presents / total_sessions *
                           100) if total_sessions > 0 else 0
        attendance_rate = round(attendance_rate, 1)

        # Grades
        valid_grades = Enrollment.objects.filter(
            clazz=clazz, status='approved', final_test__isnull=False)
        avg_grade = valid_grades.aggregate(Avg('final_test'))[
            'final_test__avg']
        avg_grade = round(avg_grade, 2) if avg_grade is not None else None

        # Grade Distribution
        grade_dist = {
            'A': valid_grades.filter(final_test__gte=8.5).count(),
            'B': valid_grades.filter(final_test__gte=7.0, final_test__lt=8.5).count(),
            'C': valid_grades.filter(final_test__gte=5.5, final_test__lt=7.0).count(),
            'D': valid_grades.filter(final_test__gte=4.0, final_test__lt=5.5).count(),
            'F': valid_grades.filter(final_test__lt=4.0).count(),
        }

        class_stats.append({
            'class_name': clazz.class_name,
            'student_count': clazz.total_enrollments,
            'attendance_rate': attendance_rate,
            'avg_grade': avg_grade if avg_grade else "N/A",
            'grade_dist': grade_dist
        })

        # Global Aggregates
        global_attendance_sum += attendance_rate
        global_attendance_count += 1
        if avg_grade:
            global_grade_sum += avg_grade
            global_grade_count += 1

        # Identify At Risk Students in this class
        enrollments = Enrollment.objects.filter(
            clazz=clazz, status='approved').select_related('student')
        for enrollment in enrollments:
            total_students_unique.add(enrollment.student.pk)

            # Student Attendance
            s_sessions = Attendance.objects.filter(
                enrollment=enrollment).count()
            s_presents = Attendance.objects.filter(
                enrollment=enrollment, status='Present').count()
            s_rate = (s_presents / s_sessions * 100) if s_sessions > 0 else 100

            # Student Grade
            s_grade = enrollment.final_test

            reasons = []
            if s_sessions > 5 and s_rate < 70:  # Only flag if enough sessions occurred
                reasons.append(f"Low Attendance ({round(s_rate)}%)")
            if s_grade is not None and s_grade < 5.0:
                reasons.append(f"Low Grade ({s_grade})")

            if reasons:
                students_at_risk.append({
                    'student_name': enrollment.student.full_name,
                    'class_name': clazz.class_name,
                    'reasons': ", ".join(reasons)
                })

    # Count Working Days (Unique dates with attendance this month)
    working_days_count = Attendance.objects.filter(
        enrollment__clazz__teacher=teacher,
        date__month=today.month,
        date__year=today.year
    ).values('date').distinct().count()

    overview = {
        'total_classes': total_classes,
        'total_students': len(total_students_unique),
        'avg_attendance_rate': round(global_attendance_sum / global_attendance_count, 1) if global_attendance_count else 0,
        'avg_grade': round(global_grade_sum / global_grade_count, 2) if global_grade_count else 0,
        'working_days': working_days_count,
    }

    context = {
        'teacher': teacher,
        'class_stats': class_stats,
        'overview': overview,
        'students_at_risk': students_at_risk,
    }
    return render(request, 'dashboard/teacher_statistics.html', context)


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
    class_distribution = Clazz.objects.values(
        'class_type__code').annotate(count=Count('class_id'))

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
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        messages.error(request, "You are not registered as a student.")
        return redirect('home')

    enrollments = student.enrollments.filter(status='approved').select_related(
        'clazz', 'clazz__class_type', 'clazz__teacher')

    # Notifications Logic
    enrolled_classes = [e.clazz for e in enrollments]

    # Fetch recent announcements and assignments for enrolled classes
    recent_announcements_qs = Announcement.objects.filter(
        clazz__in=enrolled_classes).order_by('-posted_at')
    recent_assignments_qs = Assignment.objects.filter(
        clazz__in=enrolled_classes).order_by('-created_at')

    notifications = []
    unread_count = 0

    for a in recent_announcements_qs:
        # Check read status for each announcement
        read_status, created = ContentReadStatus.objects.get_or_create(
            student=student, content_type='announcement', content_id=a.pk,
            defaults={'is_read': False}
        )
        notifications.append({
            'type': 'announcement',
            'pk': a.pk,  # Add primary key for mark as read action
            'title': a.title,
            'class_name': a.clazz.class_name,
            'date': a.posted_at,
            'icon': 'megaphone',
            'is_read': read_status.is_read,
            # Direct link
            'url': reverse('dashboard:student_class_detail', kwargs={'class_pk': a.clazz.pk})
        })
        if not read_status.is_read:
            unread_count += 1

    for a in recent_assignments_qs:
        # Check read status for each assignment
        read_status, created = ContentReadStatus.objects.get_or_create(
            student=student, content_type='assignment', content_id=a.pk,
            defaults={'is_read': False}
        )
        notifications.append({
            'type': 'assignment',
            'pk': a.pk,  # Add primary key for mark as read action
            'title': a.title,
            'class_name': a.clazz.class_name,
            'date': a.created_at,
            'icon': 'clipboard-list',
            'is_read': read_status.is_read,
            # Direct link
            'url': reverse('dashboard:student_submit_assignment', kwargs={'assignment_pk': a.pk})
        })
        if not read_status.is_read:
            unread_count += 1

    # Sort by date descending
    notifications.sort(key=lambda x: x['date'], reverse=True)
    notifications = notifications[:10]  # Top 10

    return render(request, 'dashboard/student_dashboard.html', {
        'student': student,
        'enrollments': enrollments,
        'notifications': notifications,
        'unread_count': unread_count  # Now reflects actual unread notifications
    })


@login_required
def mark_notification_as_read(request):
    if request.method == 'POST':
        try:
            student = request.user.student_profile
        except:
            return redirect('dashboard:student_dashboard')

        notification_type = request.POST.get('notification_type')
        notification_pk = request.POST.get('notification_pk')

        if not notification_type or not notification_pk:
            messages.error(request, "Invalid notification data.")
            return redirect('dashboard:student_dashboard')

        try:
            if notification_type in ['announcement', 'assignment']:
                ContentReadStatus.objects.update_or_create(
                    student=student,
                    content_type=notification_type,
                    content_id=notification_pk,
                    defaults={'is_read': True, 'read_at': timezone.now()}
                )
                messages.success(request, "Marked as read.")
            else:
                messages.error(request, "Unknown notification type.")
        except Exception as e:
            messages.error(request, f"Error marking notification as read: {e}")

    return redirect('dashboard:student_dashboard')


@login_required
def student_courses_view(request):
    try:
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        messages.error(request, "You are not registered as a student.")
        return redirect('home')

    # Fetch all classes (can be optimized to exclude enrolled ones)
    classes = Clazz.objects.all().order_by(
        'class_name').select_related('teacher', 'class_type')

    return render(request, 'dashboard/student_courses.html', {
        'classes': classes,
        'student': student
    })


@login_required
def student_pending_requests_view(request):
    try:
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        messages.error(request, "You are not registered as a student.")
        return redirect('home')

    pending_enrollments = student.enrollments.filter(status='pending')
    return render(request, 'dashboard/student_pending.html', {'student': student, 'enrollments': pending_enrollments})


@login_required
def student_achievements_view(request):
    try:
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        messages.error(request, "You are not registered as a student.")
        return redirect('home')

    enrollments = student.enrollments.all().select_related(
        'clazz', 'clazz__class_type', 'clazz__teacher')

    for enrollment in enrollments:
        # Calculate scores
        # Minitests (Average) - Treat None as 0
        m1 = enrollment.minitest1 or 0
        m2 = enrollment.minitest2 or 0
        m3 = enrollment.minitest3 or 0
        m4 = enrollment.minitest4 or 0
        mini_avg = (m1 + m2 + m3 + m4) / 4.0

        midterm = enrollment.midterm or 0
        final = enrollment.final_test or 0

        # Weighted Average: 20% Mini, 30% Mid, 50% Final
        overall = (mini_avg * 0.2) + (midterm * 0.3) + (final * 0.5)

        enrollment.overall_score_calculated = round(overall, 2)
        enrollment.is_passed = overall >= 4.0

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


@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def assign_classes_to_teacher_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        selected_class_ids = request.POST.getlist('classes')

        # 1. Unassign classes that were previously assigned but not selected anymore
        # We filter classes belonging to this teacher, EXCLUDING the ones currently selected.
        # These are the ones we want to remove.
        Clazz.objects.filter(teacher=teacher).exclude(
            pk__in=selected_class_ids).update(teacher=None)

        # 2. Assign selected classes (this will overwrite any previous teacher)
        Clazz.objects.filter(pk__in=selected_class_ids).update(teacher=teacher)

        messages.success(
            request, f"Classes assigned to {teacher.full_name} successfully!")
        return redirect('dashboard:manage_teachers')

    all_classes = Clazz.objects.all().order_by('class_name')
    return render(request, 'dashboard/assign_classes_teacher.html', {
        'teacher': teacher,
        'all_classes': all_classes
    })

# Enrollment Management


@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def manage_enrollments_view(request):
    query = request.GET.get('q')

    # Base querysets
    active_enrollments = Enrollment.objects.filter(
        status='approved').select_related('student', 'clazz')
    pending_requests = Enrollment.objects.filter(
        status='pending').select_related('student', 'clazz')

    if query:
        # Apply search to both
        search_filter = Q(student__full_name__icontains=query) | Q(
            clazz__class_name__icontains=query)
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
    requests = Enrollment.objects.filter(status='pending').select_related(
        'student', 'clazz').order_by('-enrollment_date')
    return render(request, 'dashboard/manage_requests.html', {'requests': requests})


@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def verify_payment_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.is_paid = True
    enrollment.save()
    messages.success(
        request, f"Payment verified for {enrollment.student.full_name}.")
    return redirect('dashboard:manage_enrollments')


@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def approve_request_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.status = 'approved'
    enrollment.save()

    messages.success(
        request, f"Enrollment for {enrollment.student.full_name} approved.")
    return redirect('dashboard:manage_enrollments')


@login_required
@user_passes_test(is_staff_user, login_url="accounts:login")
def reject_request_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.status = 'rejected'
    enrollment.save()
    messages.warning(
        request, f"Enrollment for {enrollment.student.full_name} rejected.")
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
    staff_members = Admin.objects.all()

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
    staff_member = get_object_or_404(Admin, pk=pk)
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
    staff_member = get_object_or_404(Admin, pk=pk)
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
            # Redirect to dashboard or class list
            return redirect('dashboard:dashboard')
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
@user_passes_test(is_teacher_or_staff, login_url="accounts:login")
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
        attendance = Attendance.objects.filter(
            enrollment=enrollment, date=date).first()
        attendance_data.append({
            'enrollment': enrollment,
            'status': attendance.status if attendance else None
        })

    is_teacher = hasattr(
        request.user, 'person') and request.user.person.role == 'teacher'
    base_template = 'dashboard/teacher_base_dashboard.html' if is_teacher else 'dashboard/base_dashboard.html'
    dashboard_url = 'dashboard:teacher_dashboard' if is_teacher else 'dashboard:dashboard'

    return render(request, 'dashboard/take_attendance.html', {
        'clazz': clazz,
        'date': date,
        'attendance_data': attendance_data,
        'base_template': base_template,
        'dashboard_url': dashboard_url
    })


@login_required
@user_passes_test(is_teacher_or_staff, login_url="accounts:login")
def enter_grades_view(request, class_pk):
    clazz = get_object_or_404(Clazz, pk=class_pk)
    enrollments = clazz.enrollments.filter(
        status='approved').select_related('student')

    if request.method == 'POST':
        for enrollment in enrollments:
            # Helper function to get float or None
            def get_score(field_name):
                val = request.POST.get(f'{field_name}_{enrollment.pk}')
                return float(val) if val else None

            enrollment.minitest1 = get_score('minitest1')
            enrollment.minitest2 = get_score('minitest2')
            enrollment.minitest3 = get_score('minitest3')
            enrollment.minitest4 = get_score('minitest4')
            enrollment.midterm = get_score('midterm')
            enrollment.final_test = get_score('final_test')
            enrollment.save()

        messages.success(request, f"Grades updated for {clazz.class_name}")
        return redirect('dashboard:enter_grades', class_pk=class_pk)

    is_teacher = hasattr(
        request.user, 'person') and request.user.person.role == 'teacher'
    base_template = 'dashboard/teacher_base_dashboard.html' if is_teacher else 'dashboard/base_dashboard.html'
    dashboard_url = 'dashboard:teacher_dashboard' if is_teacher else 'dashboard:dashboard'

    return render(request, 'dashboard/enter_grades.html', {
        'clazz': clazz,
        'enrollments': enrollments,
        'base_template': base_template,
        'dashboard_url': dashboard_url
    })


@login_required
def teacher_class_detail_view(request, class_pk):
    try:
        teacher = request.user.teacher_profile
    except:
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')

    clazz = get_object_or_404(Clazz, pk=class_pk, teacher=teacher)

    # Handle forms
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'material':
            form = MaterialForm(request.POST, request.FILES)
            if form.is_valid():
                material = form.save(commit=False)
                material.clazz = clazz
                material.save()
                messages.success(request, "Material uploaded successfully!")
                return redirect('dashboard:teacher_class_detail', class_pk=class_pk)

        elif form_type == 'announcement':
            form = AnnouncementForm(request.POST)
            if form.is_valid():
                announcement = form.save(commit=False)
                announcement.clazz = clazz
                announcement.save()
                messages.success(request, "Announcement posted successfully!")
                return redirect('dashboard:teacher_class_detail', class_pk=class_pk)

        elif form_type == 'assignment':
            form = AssignmentForm(request.POST)
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.clazz = clazz
                assignment.save()
                messages.success(request, "Assignment created successfully!")
                return redirect('dashboard:teacher_class_detail', class_pk=class_pk)

    # Fetch Data
    materials = clazz.materials.all().order_by('-uploaded_at')
    announcements = clazz.announcements.all().order_by('-posted_at')
    assignments = clazz.assignments.all().order_by('due_date')
    enrollments = clazz.enrollments.filter(
        status='approved').select_related('student')

    context = {
        'clazz': clazz,
        'materials': materials,
        'announcements': announcements,
        'assignments': assignments,
        'enrollments': enrollments,
        'material_form': MaterialForm(),
        'announcement_form': AnnouncementForm(),
        'assignment_form': AssignmentForm(),
    }
    return render(request, 'dashboard/teacher_class_detail.html', context)


@login_required
def delete_material_view(request, pk):
    try:
        teacher = request.user.teacher_profile
    except:
        return redirect('home')
    material = get_object_or_404(Material, pk=pk, clazz__teacher=teacher)
    class_pk = material.clazz.pk
    material.delete()
    messages.success(request, "Material deleted.")
    return redirect('dashboard:teacher_class_detail', class_pk=class_pk)


@login_required
def delete_announcement_view(request, pk):
    try:
        teacher = request.user.teacher_profile
    except:
        return redirect('home')
    announcement = get_object_or_404(
        Announcement, pk=pk, clazz__teacher=teacher)
    class_pk = announcement.clazz.pk
    announcement.delete()
    messages.success(request, "Announcement deleted.")
    return redirect('dashboard:teacher_class_detail', class_pk=class_pk)


@login_required
def delete_assignment_view(request, pk):
    try:
        teacher = request.user.teacher_profile
    except:
        return redirect('home')
    assignment = get_object_or_404(Assignment, pk=pk, clazz__teacher=teacher)
    class_pk = assignment.clazz.pk
    assignment.delete()
    messages.success(request, "Assignment deleted.")
    return redirect('dashboard:teacher_class_detail', class_pk=class_pk)


@login_required
def teacher_student_detail_view(request, class_pk, student_pk):
    try:
        teacher = request.user.teacher_profile
    except:
        return redirect('home')

    enrollment = get_object_or_404(
        Enrollment, clazz__pk=class_pk, student__pk=student_pk, clazz__teacher=teacher)
    student = enrollment.student
    clazz = enrollment.clazz

    # Attendance History
    attendances = Attendance.objects.filter(
        enrollment=enrollment).order_by('date')
    attendance_stats = {
        'Present': attendances.filter(status='Present').count(),
        'Absent': attendances.filter(status='Absent').count(),
        'Excused': attendances.filter(status='Excused').count(),
        'Total': attendances.count()
    }
    if attendance_stats['Total'] > 0:
        attendance_stats['rate'] = int(
            (attendance_stats['Present'] / attendance_stats['Total']) * 100)
    else:
        attendance_stats['rate'] = 0

    # Grades
    grades = {
        'Mini Test 1': enrollment.minitest1,
        'Mini Test 2': enrollment.minitest2,
        'Mini Test 3': enrollment.minitest3,
        'Mini Test 4': enrollment.minitest4,
        'Midterm': enrollment.midterm,
        'Final Test': enrollment.final_test,
    }

    context = {
        'student': student,
        'clazz': clazz,
        'enrollment': enrollment,
        'attendances': attendances,
        'attendance_stats': attendance_stats,
        'grades': grades,
    }
    return render(request, 'dashboard/teacher_student_detail.html', context)


@login_required
def teacher_assignment_submissions_view(request, assignment_pk):
    try:
        teacher = request.user.teacher_profile
    except:
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')

    assignment = get_object_or_404(
        Assignment, pk=assignment_pk, clazz__teacher=teacher)

    # Get all students enrolled in the class
    enrollments = Enrollment.objects.filter(
        clazz=assignment.clazz, status='approved').select_related('student')

    submission_data = []
    for enrollment in enrollments:
        submission = AssignmentSubmission.objects.filter(
            assignment=assignment, student=enrollment.student).first()
        form = None
        if submission:
            form = AssignmentGradingForm(instance=submission)
        else:
            form = AssignmentGradingForm()

        submission_data.append({
            'student': enrollment.student,
            'submission': submission,
            'form': form
        })

    if request.method == 'POST':
        submission_pk = request.POST.get('submission_pk')
        if submission_pk:
            submission = get_object_or_404(
                AssignmentSubmission, pk=submission_pk, assignment=assignment)
            form = AssignmentGradingForm(request.POST, instance=submission)
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"Graded {submission.student.full_name}'s submission.")
                return redirect('dashboard:teacher_assignment_submissions', assignment_pk=assignment_pk)

    return render(request, 'dashboard/teacher_assignment_submissions.html', {
        'assignment': assignment,
        'submission_data': submission_data,
        'clazz': assignment.clazz
    })


@login_required
def student_submit_assignment_view(request, assignment_pk):
    try:
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        messages.error(request, "You are not registered as a student.")
        return redirect('home')

    assignment = get_object_or_404(Assignment, pk=assignment_pk)

    # Check if student is enrolled in the class
    is_enrolled = Enrollment.objects.filter(
        student=student, clazz=assignment.clazz, status='approved').exists()
    if not is_enrolled:
        messages.error(request, "You are not enrolled in this class.")
        return redirect('dashboard:student_courses')

    submission = AssignmentSubmission.objects.filter(
        assignment=assignment, student=student).first()

    if request.method == 'POST':
        form = AssignmentSubmissionForm(
            request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = student
            sub.save()
            messages.success(request, "Assignment submitted successfully!")
            return redirect('dashboard:student_submit_assignment', assignment_pk=assignment_pk)
    else:
        form = AssignmentSubmissionForm(instance=submission)

    return render(request, 'dashboard/student_submit_assignment.html', {
        'assignment': assignment,
        'form': form,
        'submission': submission,
        'clazz': assignment.clazz
    })


@login_required
def student_class_detail_view(request, class_pk):
    try:
        student = request.user.student_profile
    except (AttributeError, Student.DoesNotExist):
        messages.error(request, "You are not registered as a student.")
        return redirect('home')

    clazz = get_object_or_404(Clazz, pk=class_pk)

    # Check enrollment
    if not Enrollment.objects.filter(student=student, clazz=clazz, status='approved').exists():
        messages.error(request, "Access denied.")
        return redirect('dashboard:student_courses')

    materials = clazz.materials.all().order_by('-uploaded_at')
    announcements = clazz.announcements.all().order_by('-posted_at')
    assignments = clazz.assignments.all().order_by('due_date')

    return render(request, 'dashboard/student_class_detail.html', {
        'clazz': clazz,
        'materials': materials,
        'announcements': announcements,
        'assignments': assignments,
    })


@login_required
def teacher_qr_generate_view(request):
    try:
        teacher = request.user.teacher_profile
    except:
        return redirect('home')

    teacher = teacher
    classes = Clazz.objects.filter(teacher=teacher)
    today = datetime.date.today()

    context = {
        'classes': classes,
        'selected_class': None,
        'qr_data': None,
        'today': today,
        'active_session': None
    }

    # Check for existing active session on GET/POST
    # logic: if teacher visits page, show current active session if exists
    active_session = AttendanceSession.objects.filter(
        clazz__teacher=teacher, date=today, is_active=True).first()

    if active_session:
        # absolute_uri = request.build_absolute_uri(reverse('dashboard:student_qr_scan', args=[token]))
        scan_url = request.build_absolute_uri(
            f"/dashboard/student/qr/scan/{active_session.token}/")
        context.update({
            'selected_class': active_session.clazz,
            'qr_data': scan_url,
            'session_token': active_session.token,
            'active_session': active_session
        })

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        if class_id:
            try:
                selected_class = Clazz.objects.get(
                    pk=class_id, teacher=teacher)

                # Deactivate old sessions for this class/day to prevent clutter
                AttendanceSession.objects.filter(
                    clazz=selected_class, date=today).update(is_active=False)

                # Create New Session
                token = uuid.uuid4().hex
                # Generate simple 4-digit passcode
                passcode = "".join([str(random.randint(0, 9))
                                   for _ in range(4)])

                session = AttendanceSession.objects.create(
                    clazz=selected_class,
                    date=today,
                    token=token,
                    passcode=passcode,
                    is_active=True
                )

                # Generate Scan URL
                scan_url = request.build_absolute_uri(
                    f"/dashboard/student/qr/scan/{token}/")

                context.update({
                    'selected_class': selected_class,
                    'qr_data': scan_url,  # Pass URL to frontend
                    'session_token': token,
                    'active_session': session
                })

                messages.success(
                    request, f"Attendance session started for {selected_class.class_name}")

            except Clazz.DoesNotExist:
                messages.error(request, "Invalid class selected.")

    return render(request, 'dashboard/teacher_qr_generate.html', context)


@login_required
def stop_qr_session_view(request, session_id):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('home')

    session = get_object_or_404(AttendanceSession, pk=session_id)

    # Security check: Ensure session belongs to teacher's class
    if session.clazz.teacher != request.user.teacher_profile:
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard:teacher_qr')

    session.is_active = False
    session.save()

    # Auto-Absent Logic: Mark all students without an attendance record as 'Absent'
    # 1. Get all approved enrollments for this class
    enrollments = Enrollment.objects.filter(
        clazz=session.clazz, status='approved')

    # 2. Get IDs of enrollments that ALREADY have an attendance record (Present, Excused, or manually marked Absent)
    existing_attendance_ids = Attendance.objects.filter(
        enrollment__in=enrollments,
        date=session.date
    ).values_list('enrollment_id', flat=True)

    # 3. Identify students who have NO record
    absent_records = []
    for enrollment in enrollments:
        if enrollment.pk not in existing_attendance_ids:
            absent_records.append(Attendance(
                enrollment=enrollment,
                date=session.date,
                status='Absent'
            ))

    # 4. Bulk create 'Absent' records
    if absent_records:
        Attendance.objects.bulk_create(absent_records)
        messages.info(
            request, f"Session stopped. {len(absent_records)} students marked as Absent.")
    else:
        messages.success(request, "Session stopped successfully.")

    return redirect('dashboard:teacher_qr')


@login_required
def student_qr_scan_view(request, token):
    if not hasattr(request.user, 'student_profile'):
        return render(request, 'dashboard/student_qr_success.html', {
            'success': False,
            'error_message': "Access denied. Students only."
        })

    student = request.user.student_profile

    # Find Session
    try:
        session = AttendanceSession.objects.get(token=token, is_active=True)
    except AttendanceSession.DoesNotExist:
        return render(request, 'dashboard/student_qr_success.html', {
            'success': False,
            'error_message': "Invalid or expired session."
        })

    # Check expiration (e.g. valid for same day)
    if session.date != datetime.date.today():
        return render(request, 'dashboard/student_qr_success.html', {
            'success': False,
            'error_message': "This session has expired."
        })

    # Check Enrollment
    enrollment = Enrollment.objects.filter(
        student=student, clazz=session.clazz, status='approved').first()
    if not enrollment:
        return render(request, 'dashboard/student_qr_success.html', {
            'success': False,
            'error_message': "You are not enrolled in this class."
        })

    # VERIFICATION LOGIC
    if request.method == 'POST':
        input_code = request.POST.get('passcode')
        if input_code == session.passcode:
            # Record Attendance
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=session.date,
                defaults={'status': 'Present'}
            )
            return render(request, 'dashboard/student_qr_success.html', {
                'success': True,
                'clazz': session.clazz,
                'date': session.date
            })
        else:
            return render(request, 'dashboard/student_verify_form.html', {
                'token': token,
                'error': "Incorrect passcode. Please try again."
            })

    # If GET, show verification form
    return render(request, 'dashboard/student_verify_form.html', {
        'token': token
    })


@login_required
def teacher_schedule_view(request):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('home')

    teacher = request.user.teacher_profile

    # Get params
    today = datetime.date.today()
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
    except ValueError:
        month = today.month
        year = today.year

    # Calculate prev/next
    first_date = datetime.date(year, month, 1)
    _, num_days = calendar.monthrange(year, month)
    last_date = datetime.date(year, month, num_days)

    prev_month = (first_date - datetime.timedelta(days=1)).month
    prev_year = (first_date - datetime.timedelta(days=1)).year
    next_month = (last_date + datetime.timedelta(days=1)).month
    next_year = (last_date + datetime.timedelta(days=1)).year

    current_month_name = calendar.month_name[month]

    # Get Classes
    classes = Clazz.objects.filter(teacher=teacher)

    # Build Calendar
    cal = calendar.Calendar(firstweekday=0)  # 0 = Monday
    calendar_data = []

    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            day_data = {
                'day': day,
                'is_today': (day == today.day and month == today.month and year == today.year),
                'events': []
            }

            if day != 0:
                current_date = datetime.date(year, month, day)
                day_name = current_date.strftime("%A")  # e.g. "Monday"

                for clazz in classes:
                    # Check date range
                    if clazz.start_date <= current_date <= clazz.end_date:
                        # Schedule is now embedded in Clazz
                        if clazz.day_of_week and day_name in clazz.day_of_week:
                            day_data['events'].append({
                                'time': f"{clazz.start_time.strftime('%H:%M') if clazz.start_time else 'TBA'} - {clazz.end_time.strftime('%H:%M') if clazz.end_time else 'TBA'}",
                                'class_name': clazz.class_name,
                                'room': clazz.room
                            })

            week_data.append(day_data)
        calendar_data.append(week_data)

    return render(request, 'dashboard/teacher_schedule.html', {
        'calendar_data': calendar_data,
        'current_month_name': current_month_name,
        'current_year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })


@login_required
def student_schedule_view(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('home')

    student = request.user.student_profile

    # Get params
    today = datetime.date.today()
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
    except ValueError:
        month = today.month
        year = today.year

    # Calculate prev/next
    first_date = datetime.date(year, month, 1)
    _, num_days = calendar.monthrange(year, month)
    last_date = datetime.date(year, month, num_days)

    prev_month = (first_date - datetime.timedelta(days=1)).month
    prev_year = (first_date - datetime.timedelta(days=1)).year
    next_month = (last_date + datetime.timedelta(days=1)).month
    next_year = (last_date + datetime.timedelta(days=1)).year

    current_month_name = calendar.month_name[month]

    # Get Enrolled Classes
    enrollments = Enrollment.objects.filter(
        student=student, status='approved').select_related('clazz')
    classes = [e.clazz for e in enrollments]

    # Build Calendar
    cal = calendar.Calendar(firstweekday=0)
    calendar_data = []

    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            day_data = {
                'day': day,
                'is_today': (day == today.day and month == today.month and year == today.year),
                'events': []
            }

            if day != 0:
                current_date = datetime.date(year, month, day)
                day_name = current_date.strftime("%A")

                for clazz in classes:
                    if clazz.start_date <= current_date <= clazz.end_date:
                        # Schedule is now embedded in Clazz
                        if clazz.day_of_week and day_name in clazz.day_of_week:
                            day_data['events'].append({
                                'time': f"{clazz.start_time.strftime('%H:%M') if clazz.start_time else 'TBA'} - {clazz.end_time.strftime('%H:%M') if clazz.end_time else 'TBA'}",
                                'class_name': clazz.class_name,
                                'room': clazz.room
                            })

            week_data.append(day_data)
        calendar_data.append(week_data)

    return render(request, 'dashboard/student_schedule.html', {
        'calendar_data': calendar_data,
        'current_month_name': current_month_name,
        'current_year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })
