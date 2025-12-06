from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Abstract base model for common person fields
class Person(models.Model):
    full_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, verbose_name="Address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Model for teachers
class Teacher(Person):
    teacher_id = models.AutoField(primary_key=True)
    qualification = models.CharField(max_length=100, verbose_name="Qualification")

    def __str__(self):
        return f"{self.full_name} ({self.teacher_id})"

# Model for students
class Student(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    student_id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"
    
# Model for Staff
class Staff(Person):
    staff_id = models.AutoField(primary_key=True, verbose_name="Staff ID")
    position = models.CharField(max_length=100, verbose_name="Position")

    def __str__(self):
        return f"{self.full_name} ({self.staff_id})"
    
# Model for Class Type
class ClassType(models.Model):
    type_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True, verbose_name="Class Type Code")
    description = models.TextField(verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

# Model for Class
class Clazz(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100, verbose_name="Class Name")
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, verbose_name="Class Type")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name="classes", verbose_name="Assigned Teacher")
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, verbose_name="Assigned Staff")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price") 
    room = models.CharField(max_length=50, verbose_name="Room")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='class_images/', default='class_images/default_class.png', verbose_name="Class Image")
    
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.class_name} ({self.class_id})"
    
class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Student")
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Class")
    enrollment_date = models.DateField(default=timezone.now, verbose_name="Enrollment Date")
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', verbose_name="Status")
    is_paid = models.BooleanField(default=False, verbose_name="Payment Status")
    # Scores
    minitest1 = models.FloatField(null=True, blank=True, verbose_name="Mini Test 1 Score")
    minitest2 = models.FloatField(null=True, blank=True, verbose_name="Mini Test 2 Score")
    minitest3 = models.FloatField(null=True, blank=True, verbose_name="Mini Test 3 Score")
    minitest4 = models.FloatField(null=True, blank=True, verbose_name="Mini Test 4 Score")
    midterm = models.FloatField(null=True, blank=True, verbose_name="Midterm Score")
    final_test = models.FloatField(null=True, blank=True, verbose_name="Final Test Score")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        unique_together = ('student', 'clazz')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        
    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.clazz.class_name}"
    
# Model for Schedule
class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    clazz = models.OneToOneField(Clazz, on_delete=models.CASCADE, related_name="schedule", verbose_name="Class")
    day_of_week = models.CharField(max_length=50, help_text="e.g., 'Monday, Wednesday, Friday'", verbose_name="Day of the Week")
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def __str__(self):
        return f"Schedule for {self.clazz.class_name}"

# Model for Attendance
class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendances", verbose_name="Enrollment")
    date = models.DateField(verbose_name="Date")
    status = models.CharField(max_length=20, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Excused', 'Excused')], verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.date} : {self.status}"
    
# Model for Feedback
class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Student")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Teacher")
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Class")
    teacher_rate = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="Teacher Rating", help_text="Rating from 1-10")
    class_rate = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="Class Rating", help_text="Rating from 1-10")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"Feedback by {self.student.full_name} for {self.teacher.full_name} in {self.clazz.class_name}"
