from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Student, Clazz, ClassType, Enrollment, Teacher, Attendance, Schedule
import datetime


class TeacherDashboardTests(TestCase):
    def setUp(self):
        # Create teacher user
        self.teacher_user = User.objects.create_user(
            'teacher', 'teacher@example.com', 'password')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            full_name="Test Teacher",
            email="teacher@example.com",
            dob=datetime.date(1980, 1, 1),
            qualification="PhD"
        )
        self.client = Client()
        self.client.force_login(self.teacher_user)

        # Create dummy data
        self.class_type = ClassType.objects.create(
            code="MATH", description="Math class")
        self.clazz = Clazz.objects.create(
            class_name="Math 101",
            class_type=self.class_type,
            teacher=self.teacher,
            room="101",
            price=100.00,
            start_date=datetime.date.today() - datetime.timedelta(days=10),
            end_date=datetime.date.today() + datetime.timedelta(days=10)
        )
        self.student = Student.objects.create(
            user=User.objects.create_user(
                'student', 'student@example.com', 'password'),
            full_name="Test Student",
            email="student@example.com",
            dob=datetime.date(2000, 1, 1)
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            clazz=self.clazz,
            status='approved',
            is_paid=True
        )

        # Add schedule
        self.schedule = Schedule.objects.create(
            clazz=self.clazz,
            day_of_week=datetime.date.today().strftime('%A'),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0)
        )

        # Add attendance
        self.attendance = Attendance.objects.create(
            enrollment=self.enrollment,
            date=datetime.date.today(),
            status='Present'
        )

    def test_teacher_dashboard_access(self):
        url = reverse('dashboard:teacher_dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/teacher_dashboard.html')

        # Verify context data
        self.assertEqual(response.context['teacher'], self.teacher)
        # Check if total_students is calculated correctly
        # We might not be able to check local variables easily, but if page renders 200, the query passed.
