
from django.urls import path
from .views import SoUserAPIView

urlpatterns =[
    path('so-users/', SoUserAPIView.as_view()),
]
