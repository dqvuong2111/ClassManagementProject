from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SimpleSignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='student', label="I am a")
    full_name = forms.CharField(max_length=100, required=True)
    dob = forms.DateField(required=True, widget=forms.DateInput(
        attrs={'type': 'date'}), label="Date of Birth")
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=255, required=True)
    qualification = forms.CharField(
        max_length=100, required=False, help_text="Required if signing up as a Teacher")

    def __init__(self, *args, **kwargs):
        super(SimpleSignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'role':  # Don't add form-control to radio buttons
                self.fields[field].widget.attrs.update({
                    'class': 'form-control rounded-pill'
                })

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        qualification = cleaned_data.get('qualification')

        if role == 'teacher' and not qualification:
            self.add_error('qualification',
                           "Qualification is required for teachers.")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    class Meta:
        model = User
        fields = ("username", "email")
