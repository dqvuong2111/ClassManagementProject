from django.contrib import admin
from .models import (
    Admin,
    Teacher,
    Student,
    ClassType,
    Clazz,
    Enrollment,
    Attendance,
    AttendanceSession,
    Feedback,
    Message,
    Material,
    Announcement,
    Assignment,
    AssignmentSubmission,
    ContentReadStatus
)


class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'full_name', 'position', 'email')
    search_fields = ('full_name', 'email')


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'full_name', 'qualification', 'email')
    search_fields = ('full_name', 'email')


class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'email', 'phone_number')
    search_fields = ('full_name', 'email')


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'get_student_name',
                    'get_class_name', 'enrollment_date', 'status')
    list_filter = ('status', 'is_paid')

    def get_student_name(self, obj):
        return obj.student.full_name
    get_student_name.short_description = 'Student'

    def get_class_name(self, obj):
        return obj.clazz.class_name
    get_class_name.short_description = 'Class'


class ClazzAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'class_name', 'teacher',
                    'day_of_week', 'start_time')
    list_filter = ('class_type',)
    search_fields = ('class_name',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read',)


# Register models
admin.site.register(Admin, AdminModelAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(ClassType)
admin.site.register(Clazz, ClazzAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Attendance)
admin.site.register(AttendanceSession)
admin.site.register(Feedback)
admin.site.register(Message, MessageAdmin)
admin.site.register(Material)
admin.site.register(Announcement)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(ContentReadStatus)
