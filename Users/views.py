from rest_framework.views import APIView
from rest_framework.response import Response
from .models.Timetables import Timetable
from .models.subject import Subject
from .models.souser import SoUser
from .serializers.so_user_serializer import SoUserSerializer
from Classes.models.SoClasses import SoClasses
from Students.models.SoStudents import SoStudent
from Classes.serializers.so_classes_serializer import SoClassesSerializer
from .serializers.subject_serializer import SubjectSerializer
from .serializers.timetable_serializers import TimetableSerializer
from Parents.models.SoStudentParents import SoStudentParents
from Users.serializers.so_user_serializer import SoUserSerializer
from django.contrib.auth.hashers import make_password
from datetime import datetime
from Parents.models.SoCheckins import SoCheckins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from Users.models import SoUser
from django.db.models import Q
import uuid
import json
from utils.decorator import logger

class SoUserAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Lấy danh sách tất cả người dùng (isDeleted=False)",
        responses={200: SoUserSerializer(many=True)}
    )
    # @logger(level="log", name="get_users")
    def get(self, request, *args, **kwargs):
        users = SoUser.objects.filter(isDeleted=False)
        serializer = SoUserSerializer(users, many=True)
        return Response(serializer.data)
        
    @swagger_auto_schema(
        request_body=SoUserSerializer,
        responses={201: SoUserSerializer}
    )
    # @logger(level="log", name="create_user")
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user = SoUser.objects.create(
                id=str(uuid.uuid4()),
                username=data.get("username"),
                password=make_password(data.get("password")),
                name=data.get("name"),
                dob=data.get("dob"),
                phone=data.get("phone"),
                email=data.get("email"),
                address=data.get("address"),
                nationalId=data.get("nationalId"),
                avt=data.get("avt"),
                soRoleIds=json.dumps(data.get("soRoleIds", [])),
                createdBy=data.get("createdBy"),
                updatedBy=data.get("updatedBy"),
            )
            return Response({"message": "Thêm người dùng thành công", "user": SoUserSerializer(user).data})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=SoUserSerializer,
        responses={200: SoUserSerializer}
    )
    # @logger(level="log", name="update_user")
    def patch(self, request, *args, **kwargs):
        try:
            data = request.data
            user_id = data.get("id")
            if not user_id:
                return Response({"error": "Thiếu ID người dùng"}, status=400)
            user = SoUser.objects.get(id=user_id)

            for field in ['username', 'name', 'dob', 'phone', 
                'email', 'address', 'nationalId', 'avt', 'createdBy', 'updatedBy']:
                if field in data:
                    setattr(user, field, data[field])
            if 'password' in data:
                user.password = make_password(data['password'])
            if 'soRoleIds' in data:
                user.soRoleIds = json.dumps(data['soRoleIds'])

            user.save()
            return Response({"message": "Cập nhật người dùng thành công", "user": SoUserSerializer(user).data})
        except SoUser.DoesNotExist:
            return Response({"error": "Không tìm thấy người dùng"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='ID người dùng cần xóa')
            },
            required=['id']
        ),
        responses={200: openapi.Response('Xoá thành công')}
    )
    # @logger(level="log", name="delete_user")
    def delete(self, request, *args, **kwargs):
        try:
            user_id = request.data.get("id")
            if not user_id:
                return Response({"error": "Thiếu ID người dùng"}, status=400)
            user = SoUser.objects.get(id=user_id)
            user.isDeleted = True
            user.save()
            return Response({"message": "Đã xoá người dùng."})
        except SoUser.DoesNotExist:
            return Response({"error": "Không tìm thấy người dùng"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

