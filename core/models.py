from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Role-Specific Models


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_profile')
    full_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    email = models.EmailField(verbose_name="Email Address")
    address = models.CharField(max_length=255, verbose_name="Address")
    position = models.CharField(
        max_length=100, verbose_name="Position", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

    def __str__(self):
        return f"{self.full_name} (Admin)"


class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='teacher_profile')
    full_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    email = models.EmailField(verbose_name="Email Address")
    address = models.CharField(max_length=255, verbose_name="Address")
    qualification = models.CharField(
        max_length=100, verbose_name="Qualification", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self):
        return f"{self.full_name} (Teacher)"


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    full_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    email = models.EmailField(verbose_name="Email Address")
    address = models.CharField(max_length=255, verbose_name="Address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.full_name} (Student)"

# Other Models


class ClassType(models.Model):
    type_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True,
                            verbose_name="Class Type Code")
    description = models.TextField(verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Clazz(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100, verbose_name="Class Name")
    class_type = models.ForeignKey(
        ClassType, on_delete=models.CASCADE, verbose_name="Class Type")

    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,
                                related_name="classes_taught", verbose_name="Assigned Teacher")
    staff = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True,
                              related_name="classes_managed", verbose_name="Assigned Staff")

    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Price")
    room = models.CharField(max_length=50, verbose_name="Room")
    image = models.ImageField(
        upload_to='class_images/', default='class_images/default_class.png', verbose_name="Class Image")

    day_of_week = models.CharField(
        max_length=100, help_text="e.g., 'Monday, Wednesday'", verbose_name="Days of Week", null=True, blank=True)
    start_time = models.TimeField(
        verbose_name="Start Time", null=True, blank=True)
    end_time = models.TimeField(verbose_name="End Time", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.class_name} ({self.class_id})"


class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Student")
    clazz = models.ForeignKey(
        Clazz, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Class")
    enrollment_date = models.DateField(
        default=timezone.now, verbose_name="Enrollment Date")
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), (
        'approved', 'Approved'), ('rejected', 'Rejected')], default='pending', verbose_name="Status")
    is_paid = models.BooleanField(default=False, verbose_name="Payment Status")

    minitest1 = models.FloatField(
        null=True, blank=True, verbose_name="Mini Test 1")
    minitest2 = models.FloatField(
        null=True, blank=True, verbose_name="Mini Test 2")
    minitest3 = models.FloatField(
        null=True, blank=True, verbose_name="Mini Test 3")
    minitest4 = models.FloatField(
        null=True, blank=True, verbose_name="Mini Test 4")
    midterm = models.FloatField(null=True, blank=True, verbose_name="Midterm")
    final_test = models.FloatField(
        null=True, blank=True, verbose_name="Final Test")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'clazz')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.clazz.class_name}"


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="attendances", verbose_name="Enrollment")
    date = models.DateField(verbose_name="Date")
    status = models.CharField(max_length=20, choices=[(
        'Present', 'Present'), ('Absent', 'Absent'), ('Excused', 'Excused')], verbose_name="Status")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.date} : {self.status}"


class AttendanceSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE,
                              related_name="attendance_sessions", verbose_name="Class")
    date = models.DateField(default=timezone.now, verbose_name="Date")
    token = models.CharField(max_length=64, unique=True,
                             verbose_name="Session Token")
    passcode = models.CharField(
        max_length=4, default='0000', verbose_name="Session Passcode")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR Session for {self.clazz.class_name} on {self.date}"


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Student")
    clazz = models.ForeignKey(
        Clazz, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Class")

    teacher_rate = models.DecimalField(
        max_digits=3, decimal_places=2, verbose_name="Teacher Rating", help_text="Rating from 1-10")
    class_rate = models.DecimalField(
        max_digits=3, decimal_places=2, verbose_name="Class Rating", help_text="Rating from 1-10")
    comment = models.TextField(blank=True, verbose_name="Comment")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    @property
    def derived_teacher(self):
        return self.clazz.teacher

    def __str__(self):
        return f"Feedback by {self.student.full_name} for {self.clazz.class_name}"


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages", verbose_name="Sender")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name="received_messages", verbose_name="Recipient")
    subject = models.CharField(max_length=255, verbose_name="Subject")
    body = models.TextField(verbose_name="Body")
    is_read = models.BooleanField(default=False, verbose_name="Is Read")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.subject}"


class Material(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    file = models.FileField(upload_to='class_materials/', verbose_name="File")
    clazz = models.ForeignKey(
        Clazz, related_name='materials', on_delete=models.CASCADE, verbose_name="Class")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.clazz.class_name})"


class Announcement(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    content = models.TextField(verbose_name="Content")
    clazz = models.ForeignKey(
        Clazz, related_name='announcements', on_delete=models.CASCADE, verbose_name="Class")
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.clazz.class_name})"


class Assignment(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    due_date = models.DateTimeField(verbose_name="Due Date")
    clazz = models.ForeignKey(
        Clazz, related_name='assignments', on_delete=models.CASCADE, verbose_name="Class")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.clazz.class_name})"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, related_name='submissions', on_delete=models.CASCADE, verbose_name="Assignment")
    student = models.ForeignKey(
        Student, related_name='submissions', on_delete=models.CASCADE, verbose_name="Student")
    submission_file = models.FileField(
        upload_to='assignment_submissions/', verbose_name="Submission File")
    submitted_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Submitted At")
    grade = models.FloatField(null=True, blank=True, verbose_name="Grade")
    feedback = models.TextField(blank=True, verbose_name="Feedback")

    class Meta:
        unique_together = ('assignment', 'student')
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"


class ContentReadStatus(models.Model):
    CONTENT_TYPES = [
        ('announcement', 'Announcement'),
        ('assignment', 'Assignment'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                                related_name='read_statuses', verbose_name="Student", null=True, blank=True)
    content_type = models.CharField(
        max_length=20, choices=CONTENT_TYPES, verbose_name="Content Type")
    content_id = models.IntegerField(verbose_name="Content ID")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    content_object_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    content_object = GenericForeignKey('content_object_type', 'content_id')

    class Meta:
        unique_together = ('student', 'content_type', 'content_id')
        verbose_name = "Content Read Status"
        verbose_name_plural = "Content Read Statuses"

    def __str__(self):
        return f"{self.student.full_name} - {self.content_type} {self.content_id} (Read: {self.is_read})"
