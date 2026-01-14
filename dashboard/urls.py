from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('documents/', views.admin_documents_view, name='admin_documents'),
    path('statistics/', views.admin_statistics_view, name='admin_statistics'),
    path('', views.admin_dashboard_view, name='dashboard'),

    # Teacher Dashboard
    path('teacher/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('teacher/assignments/', views.teacher_assignments_view,
         name='teacher_assignments'),
    path('teacher/assignments/create/', views.teacher_create_assignment_view,
         name='teacher_create_assignment'),
    path('teacher/schedule/', views.teacher_schedule_view, name='teacher_schedule'),
    path('teacher/statistics/', views.teacher_statistics_view,
         name='teacher_statistics'),
    path('teacher/feedback/', views.teacher_feedback_list_view,
         name='teacher_feedback'),
    path('teacher/qr/', views.teacher_qr_generate_view, name='teacher_qr'),
    path('teacher/qr/stop/<int:session_id>/',
         views.stop_qr_session_view, name='stop_qr_session'),
    path('messages/', views.messages_view, name='messages'),

    path('teacher/class/<int:class_pk>/',
         views.teacher_class_detail_view, name='teacher_class_detail'),
    path('teacher/material/delete/<int:pk>/',
         views.delete_material_view, name='delete_material'),
    path('teacher/announcement/delete/<int:pk>/',
         views.delete_announcement_view, name='delete_announcement'),
    path('teacher/assignment/delete/<int:pk>/',
         views.delete_assignment_view, name='delete_assignment'),
    path('teacher/assignment/<int:assignment_pk>/submissions/',
         views.teacher_assignment_submissions_view, name='teacher_assignment_submissions'),
    path('teacher/class/<int:class_pk>/student/<int:student_pk>/',
         views.teacher_student_detail_view, name='teacher_student_detail'),

    path('student/', views.student_dashboard_view, name='student_dashboard'),
    path('student/courses/', views.student_courses_view, name='student_courses'),
    path('student/class/<int:class_pk>/',
         views.student_class_detail_view, name='student_class_detail'),
    path('student/class/<int:class_pk>/feedback/',
         views.student_give_feedback_view, name='student_give_feedback'),
    path('student/assignment/<int:assignment_pk>/submit/',
         views.student_submit_assignment_view, name='student_submit_assignment'),
    path('student/qr/scan/<str:token>/',
         views.student_qr_scan_view, name='student_qr_scan'),
    path('student/schedule/', views.student_schedule_view, name='student_schedule'),
    path('student/pending/', views.student_pending_requests_view,
         name='student_pending'),
    path('student/achievements/', views.student_achievements_view,
         name='student_achievements'),
    path('student/notifications/mark-read/',
         views.mark_notification_as_read, name='mark_notification_as_read'),

    # Class Management
    path('add_class/', views.add_class_view, name='add_class'),
    path('edit_class/<int:pk>/', views.edit_class_view, name='edit_class'),
    path('delete_class/<int:pk>/', views.delete_class_view, name='delete_class'),
    path('class/<int:class_pk>/schedule/',
         views.manage_schedule_view, name='manage_schedule'),
    path('class/<int:class_pk>/attendance/',
         views.take_attendance_view, name='take_attendance'),
    path('class/<int:class_pk>/grades/',
         views.enter_grades_view, name='enter_grades'),

    # Student Management
    path('students/', views.manage_students_view, name='manage_students'),
    path('students/add/', views.add_student_view, name='add_student'),
    path('students/edit/<int:pk>/', views.edit_student_view, name='edit_student'),
    path('students/delete/<int:pk>/',
         views.delete_student_view, name='delete_student'),

    # Teacher Management
    path('teachers/', views.manage_teachers_view, name='manage_teachers'),
    path('teachers/add/', views.add_teacher_view, name='add_teacher'),
    path('teachers/edit/<int:pk>/', views.edit_teacher_view, name='edit_teacher'),
    path('teachers/assign/<int:pk>/', views.assign_classes_to_teacher_view,
         name='assign_classes_teacher'),
    path('teachers/delete/<int:pk>/',
         views.delete_teacher_view, name='delete_teacher'),

    # Enrollment Management
    path('enrollments/', views.manage_enrollments_view, name='manage_enrollments'),
    path('enrollments/requests/', views.manage_requests_view, name='manage_requests'),
    path('enrollments/approve/<int:pk>/',
         views.approve_request_view, name='approve_request'),
    path('enrollments/verify-payment/<int:pk>/',
         views.verify_payment_view, name='verify_payment'),
    path('enrollments/reject/<int:pk>/',
         views.reject_request_view, name='reject_request'),
    path('enrollments/add/', views.add_enrollment_view, name='add_enrollment'),
    path('enrollments/delete/<int:pk>/',
         views.delete_enrollment_view, name='delete_enrollment'),

    # Staff Management
    path('staff/', views.manage_staff_view, name='manage_staff'),
    path('staff/add/', views.add_staff_view, name='add_staff'),
    path('staff/edit/<int:pk>/', views.edit_staff_view, name='edit_staff'),
    path('staff/delete/<int:pk>/', views.delete_staff_view, name='delete_staff'),

    # Class Type Management
    path('class-types/', views.manage_class_types_view, name='manage_class_types'),
    path('class-types/add/', views.add_class_type_view, name='add_class_type'),
    path('class-types/edit/<int:pk>/',
         views.edit_class_type_view, name='edit_class_type'),
    path('class-types/delete/<int:pk>/',
         views.delete_class_type_view, name='delete_class_type'),
]
