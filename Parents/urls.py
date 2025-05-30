from django.urls import path
from .views import  SoParentsAPIView, SoStudentParentsAPI


urlpatterns =[
    path('so-parents/', SoParentsAPIView.as_view(), name='so-parents-api'),
    path('so-student-parents/', SoStudentParentsAPI.as_view()),
    path('so-student-parents/<str:id>', SoStudentParentsAPI.as_view()),
]
