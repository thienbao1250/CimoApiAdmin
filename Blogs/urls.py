from django.urls import path
from Blogs.views import SoBlogsAPI

urlpatterns = [
    path('so-blogs/', SoBlogsAPI.as_view()),
    path('so-blogs/<str:id>', SoBlogsAPI.as_view()),  # DELETE
]
