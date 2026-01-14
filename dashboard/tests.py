from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Student, Clazz, ClassType, Enrollment, Teacher


class AdminEnrollmentTests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            'admin', 'admin@example.com', 'password')
        self.client = Client()
        self.client.force_login(self.admin_user)

        # Create dummy data
        self.teacher = Teacher.objects.create(
            user=User.objects.create_user(
                'teacher', 'teacher@example.com', 'password'),
            full_name="Test Teacher",
            email="teacher@example.com"
        )
        self.class_type = ClassType.objects.create(
            code="MATH", name="Mathematics", description="Math class", price=100.00)
        self.clazz = Clazz.objects.create(
            class_name="Math 101",
            class_type=self.class_type,
            teacher=self.teacher,
            room="101"
        )
        self.student = Student.objects.create(
            user=User.objects.create_user(
                'student', 'student@example.com', 'password'),
            full_name="Test Student",
            email="student@example.com"
        )

    def test_approve_request_paid(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            clazz=self.clazz,
            status='pending',
            is_paid=False
        )

        url = reverse('dashboard:approve_request', args=[enrollment.pk])
        response = self.client.get(url + '?paid=true')

        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'approved')
        self.assertTrue(enrollment.is_paid)
        self.assertRedirects(response, reverse('dashboard:manage_enrollments'))

    def test_approve_request_unpaid(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            clazz=self.clazz,
            status='pending',
            is_paid=False
        )

        url = reverse('dashboard:approve_request', args=[enrollment.pk])
        response = self.client.get(url + '?paid=false')

        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'approved')
        self.assertFalse(enrollment.is_paid)
        self.assertRedirects(response, reverse('dashboard:manage_enrollments'))
