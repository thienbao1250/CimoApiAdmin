
from django.urls import path
from .views import SoUserAPIView, ImportExcelAPIView, export_excel

urlpatterns =[
    path('so-users/<str:user_id>', SoUserAPIView.as_view()),
    path('so-users/', SoUserAPIView.as_view()),
    path('import-excel/', ImportExcelAPIView.as_view()),
    path('export-excel/', export_excel.as_view()),
]
