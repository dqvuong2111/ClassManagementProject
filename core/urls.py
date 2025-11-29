from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('classes/', views.class_list, name='class_list'),
    path('class/<int:pk>/', views.class_detail, name='class_detail'),
]