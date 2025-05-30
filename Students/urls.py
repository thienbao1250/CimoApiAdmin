# Parents/urls.py
from django.urls import path
from Students.views import SoStudentAPIView

urlpatterns =[
    path('so-students/', SoStudentAPIView.as_view(), name='so-student'),
]
