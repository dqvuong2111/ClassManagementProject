from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('documents/', views.admin_documents_view, name='admin_documents'),
    path('statistics/', views.admin_statistics_view, name='admin_statistics'),
    path('', views.admin_dashboard_view, name='dashboard'),
    path('student/', views.student_dashboard_view, name='student_dashboard'),
    path('student/courses/', views.student_courses_view, name='student_courses'),
    path('student/schedule/', views.student_schedule_view, name='student_schedule'),
    path('student/achievements/', views.student_achievements_view, name='student_achievements'),
    
    # Class Management
    path('add_class/', views.add_class_view, name='add_class'),
    path('edit_class/<int:pk>/', views.edit_class_view, name='edit_class'),
    path('delete_class/<int:pk>/', views.delete_class_view, name='delete_class'),
    path('class/<int:class_pk>/schedule/', views.manage_schedule_view, name='manage_schedule'),
    path('class/<int:class_pk>/attendance/', views.take_attendance_view, name='take_attendance'),

    # Student Management
    path('students/', views.manage_students_view, name='manage_students'),
    path('students/add/', views.add_student_view, name='add_student'),
    path('students/edit/<int:pk>/', views.edit_student_view, name='edit_student'),
    path('students/delete/<int:pk>/', views.delete_student_view, name='delete_student'),

    # Teacher Management
    path('teachers/', views.manage_teachers_view, name='manage_teachers'),
    path('teachers/add/', views.add_teacher_view, name='add_teacher'),
    path('teachers/edit/<int:pk>/', views.edit_teacher_view, name='edit_teacher'),
    path('teachers/delete/<int:pk>/', views.delete_teacher_view, name='delete_teacher'),

    # Enrollment Management
    path('enrollments/', views.manage_enrollments_view, name='manage_enrollments'),
    path('enrollments/add/', views.add_enrollment_view, name='add_enrollment'),
    path('enrollments/delete/<int:pk>/', views.delete_enrollment_view, name='delete_enrollment'),

    # Staff Management
    path('staff/', views.manage_staff_view, name='manage_staff'),
    path('staff/add/', views.add_staff_view, name='add_staff'),
    path('staff/edit/<int:pk>/', views.edit_staff_view, name='edit_staff'),
    path('staff/delete/<int:pk>/', views.delete_staff_view, name='delete_staff'),

    # Class Type Management
    path('class-types/', views.manage_class_types_view, name='manage_class_types'),
    path('class-types/add/', views.add_class_type_view, name='add_class_type'),
    path('class-types/edit/<int:pk>/', views.edit_class_type_view, name='edit_class_type'),
    path('class-types/delete/<int:pk>/', views.delete_class_type_view, name='delete_class_type'),
]