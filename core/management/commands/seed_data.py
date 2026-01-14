from django.core.management.base import BaseCommand
from datetime import date, time
from django.contrib.auth.models import User
from core.models import Teacher, Student, Staff, ClassType, Clazz, Enrollment, Schedule, Feedback


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        self.seed_data()
        self.stdout.write(self.style.SUCCESS('Data seeded successfully!'))

    def seed_data(self):
        # Create Users for Students
        user1, _ = User.objects.get_or_create(username='ada.lovelace', defaults={
                                              'email': 'ada.lovelace@example.com', 'password': 'password'})
        user2, _ = User.objects.get_or_create(username='charles.babbage', defaults={
                                              'email': 'charles.babbage@example.com', 'password': 'password'})

        # Create Teachers
        teacher1, _ = Teacher.objects.get_or_create(email="alan.turing@example.com", defaults={
                                                    'full_name': "Dr. Alan Turing", 'dob': "1912-06-23", 'phone_number': "123-456-7890", 'address': "Bletchley Park", 'qualification': "Ph.D. in Mathematics"})
        teacher2, _ = Teacher.objects.get_or_create(email="grace.hopper@example.com", defaults={
                                                    'full_name': "Grace Hopper", 'dob': "1906-12-09", 'phone_number': "098-765-4321", 'address': "Arlington, VA", 'qualification': "Ph.D. in Mathematics"})

        # Create Students
        student1, _ = Student.objects.get_or_create(email="ada.lovelace@example.com", defaults={
                                                    'full_name': "Ada Lovelace", 'dob': "1815-12-10", 'phone_number': "111-222-3333", 'address': "London, England", 'user': user1})
        student2, _ = Student.objects.get_or_create(email="charles.babbage@example.com", defaults={
                                                    'full_name': "Charles Babbage", 'dob': "1791-12-26", 'phone_number': "444-555-6666", 'address': "London, England", 'user': user2})

        # Create Staff
        staff1, _ = Staff.objects.get_or_create(email="john.neumann@example.com", defaults={
                                                'full_name': "John von Neumann", 'dob': "1903-12-28", 'phone_number': "777-888-9999", 'address': "Princeton, NJ", 'position': "Administrator"})

        # Create Class Types
        math_type, _ = ClassType.objects.get_or_create(
            code="MATH", defaults={'description': "Mathematics Courses"})
        cs_type, _ = ClassType.objects.get_or_create(
            code="CS", defaults={'description': "Computer Science Courses"})

        # Create Classes
        class1, _ = Clazz.objects.get_or_create(class_name="Introduction to Python", defaults={'class_type': cs_type, 'teacher': teacher2, 'staff': staff1, 'start_date': date(
            2025, 9, 1), 'end_date': date(2025, 12, 20), 'price': "199.99", 'room': "Room 101"})
        class2, _ = Clazz.objects.get_or_create(class_name="Advanced Algorithms", defaults={'class_type': cs_type, 'teacher': teacher1, 'staff': staff1, 'start_date': date(
            2025, 9, 1), 'end_date': date(2025, 12, 20), 'price': "299.99", 'room': "Room 102"})
        class3, _ = Clazz.objects.get_or_create(class_name="Calculus I", defaults={'class_type': math_type, 'teacher': teacher1, 'staff': staff1, 'start_date': date(
            2025, 9, 1), 'end_date': date(2025, 12, 20), 'price': "249.99", 'room': "Room 201"})

        # Create Enrollments
        Enrollment.objects.get_or_create(student=student1, clazz=class1)
        Enrollment.objects.get_or_create(student=student2, clazz=class1)
        Enrollment.objects.get_or_create(student=student1, clazz=class2)

        # Create Schedules
        Schedule.objects.get_or_create(clazz=class1, defaults={
                                       'day_of_week': 'Monday, Wednesday', 'start_time': time(10, 0), 'end_time': time(11, 30)})
        Schedule.objects.get_or_create(clazz=class2, defaults={
                                       'day_of_week': 'Tuesday, Thursday', 'start_time': time(14, 0), 'end_time': time(15, 30)})
        Schedule.objects.get_or_create(clazz=class3, defaults={
                                       'day_of_week': 'Friday', 'start_time': time(9, 0), 'end_time': time(12, 0)})

        # Create Feedback
        Feedback.objects.get_or_create(student=student1, teacher=teacher2, clazz=class1, defaults={
                                       'teacher_rate': "9.5", 'class_rate': "8.0"})
        Feedback.objects.get_or_create(student=student2, teacher=teacher2, clazz=class1, defaults={
                                       'teacher_rate': "9.0", 'class_rate': "8.5"})
        Feedback.objects.get_or_create(student=student1, teacher=teacher1, clazz=class2, defaults={
                                       'teacher_rate': "9.8", 'class_rate': "9.0"})
