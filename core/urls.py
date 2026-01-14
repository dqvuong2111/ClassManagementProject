from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('classes/', views.class_list, name='class_list'),
    path('class/<int:pk>/', views.class_detail, name='class_detail'),
    path('enroll/<int:class_id>/', views.enroll_student, name='enroll_student'),
    path('features/', views.features, name='features'),
]
