from django import forms
from core.models import Clazz, Teacher, Student, Admin, Enrollment, ClassType, Attendance, Material, Announcement, Assignment, AssignmentSubmission, Message, Feedback


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            else:
                field.widget.attrs['class'] = 'form-input'


class ClassForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Clazz
        fields = '__all__'
        exclude = ('teacher', 'staff', 'image')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class TeacherForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['full_name', 'dob', 'phone_number',
                  'email', 'address', 'qualification']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }


class StudentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'dob', 'phone_number', 'email', 'address']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }


class StaffForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['full_name', 'dob', 'phone_number',
                  'email', 'address', 'position']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }


class EnrollmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = '__all__'
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ClassTypeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ClassType
        fields = '__all__'


class ScheduleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Clazz
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class AttendanceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Attendance
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class MaterialForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'file']


class AnnouncementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }


class AssignmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AssignmentSubmissionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file']


class AssignmentGradingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['grade', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 2}),
        }


class AssignmentCreateForm(BootstrapFormMixin, forms.ModelForm):
    clazz = forms.ModelChoiceField(
        queryset=Clazz.objects.none(), label="Class")

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'clazz']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['clazz'].queryset = Clazz.objects.filter(
                teacher=teacher)


class MessageForm(BootstrapFormMixin, forms.ModelForm):
    recipient_username = forms.CharField(label="Recipient Username")

    class Meta:
        model = Message
        fields = ['recipient_username', 'subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_recipient_username(self):
        username = self.cleaned_data['recipient_username']
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError("User not found.")


class FeedbackForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['teacher_rate', 'class_rate', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'teacher_rate': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'class_rate': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }
