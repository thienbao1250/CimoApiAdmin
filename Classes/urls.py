from rest_framework.routers import DefaultRouter
from django.urls import path, include
from Classes.views import SoClassesAPI, SoClassesCountAPI

urlpatterns =[
    path('so-classes/', SoClassesAPI.as_view(), name='so-classes'),
    path('classes/count', SoClassesCountAPI.as_view(), name='so-classes-count'),
    path('so-classes/<str:class_id>', SoClassesAPI.as_view(), name='so-classes'),
]
