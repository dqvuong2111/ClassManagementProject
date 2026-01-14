from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Clazz, Student, ClassType, Teacher, Enrollment
from django.utils import timezone


class EnrollmentTests(TestCase):
    def setUp(self):
        # Create User and Student
        self.user = User.objects.create_user(
            username='student', password='password')
        self.student = Student.objects.create(
            user=self.user,
            full_name='Test Student',
            dob='2000-01-01',
            phone_number='1234567890',
            email='student@example.com',
            address='123 Test St'
        )

        # Create ClassType and Teacher (required for Clazz)
        self.class_type = ClassType.objects.create(
            code='MATH', description='Math Class')
        self.teacher = Teacher.objects.create(
            full_name='Test Teacher',
            dob='1980-01-01',
            phone_number='0987654321',
            email='teacher@example.com',
            address='456 Teach St',
            qualification='PhD'
        )

        # Create Class
        self.clazz = Clazz.objects.create(
            class_name='Algebra 101',
            class_type=self.class_type,
            teacher=self.teacher,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            price=100.00,
            room='101'
        )

    def test_enroll_student_success(self):
        self.client.login(username='student', password='password')
        response = self.client.get(
            reverse('enroll_student', args=[self.clazz.class_id]))

        # Check redirection
        self.assertRedirects(response, reverse('dashboard:student_dashboard'))

        # Check enrollment created
        self.assertTrue(Enrollment.objects.filter(
            student=self.student, clazz=self.clazz).exists())

    def test_enroll_student_already_enrolled(self):
        # Create initial enrollment
        Enrollment.objects.create(student=self.student, clazz=self.clazz)

        self.client.login(username='student', password='password')
        response = self.client.get(
            reverse('enroll_student', args=[self.clazz.class_id]))

        # Should redirect back to class detail with warning
        self.assertRedirects(response, reverse(
            'class_detail', args=[self.clazz.class_id]))

        # Check still only 1 enrollment
        self.assertEqual(Enrollment.objects.filter(
            student=self.student, clazz=self.clazz).count(), 1)

    def test_enroll_student_not_logged_in(self):
        response = self.client.get(
            reverse('enroll_student', args=[self.clazz.class_id]))
        # Should redirect to login page
        # Django default login url is /accounts/login/ or whatever is in settings.
        # We just check it's a redirect (302) and not 200
        self.assertEqual(response.status_code, 302)
