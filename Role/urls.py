from django.urls import path
from Role.views import SoRoleAPI, SoRoleCountAPI

urlpatterns = [
    path('so-roles/', SoRoleAPI.as_view(), name='so-roles'),
    path('so-roles/count', SoRoleCountAPI.as_view(), name='so-roles-count'),
]
