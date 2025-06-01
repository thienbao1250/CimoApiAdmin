from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from datetime import datetime
from .models.SoStudents import SoStudent
from .models.SoStudentOff import SoStudentOff
# from .serializers
from Parents.models import SoCheckins,SoParents,SoStudentParents
from Classes.serializers.so_classes_serializer import SoClassesSerializer
from Classes.serializers.so_class_users_serializer import SoClassUsersSerializer
from .serializers.so_student_off_serializer import SoStudentOffSerializer
from Classes.models.SoClasses import SoClasses
from Classes.models.SoClassUsers import SoClassUsers
from Users.models.souser import SoUser
from Users.serializers import SoUserSerializer
from collections import defaultdict
from Auth.views import veriry_token
import calendar
from Students.serializers.so_students_serializer import SoStudentsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
import json
from utils.decorator import logger

class SoStudentAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Lấy danh sách tất cả học sinh (isDeleted=False)",
        responses={200: SoStudentsSerializer(many=True)}
    )
    # @logger(level="log", name="get_students")
    def get(self, request, *args, **kwargs):
        students = SoStudent.objects.filter(isDeleted=False)
        serializer = SoStudentsSerializer(students, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SoStudentsSerializer,
        responses={201: SoStudentsSerializer}
    )
    # @logger(level="log", name="create_student")
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            student = SoStudent.objects.create(
                id=data.get("id") or str(uuid.uuid4()),
                name=data.get("name"),
                dob=data.get("dob"),
                gender=data.get("gender"),
                phone=data.get("phone"),
                email=data.get("email"),
                address=data.get("address"),
                nationalId=data.get("nationalId"),
                avt=data.get("avt"),
                soClassId=data.get("soClassId"),
                isDeleted=data.get("isDeleted", False),
                createdBy=data.get("createdBy"),
                updatedBy=data.get("updatedBy"),
                createdDate=data.get("createdDate"),
                updatedDate=data.get("updatedDate"),
            )
            return Response({
                "message": "Thêm học sinh thành công",
                "student": SoStudentsSerializer(student).data
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=SoStudentsSerializer,
        responses={200: SoStudentsSerializer}
    )
    # @logger(level="log", name="update_student")
    def patch(self, request, *args, **kwargs):
        try:
            data = request.data
            student_id = data.get("id")
            if not student_id:
                return Response({"error": "Thiếu ID học sinh"}, status=400)
            student = SoStudent.objects.get(id=student_id)

            for field in ['name', 'dob', 'gender', 'phone', 'email', 'address',
                          'nationalId', 'avt', 'soClassId', 'createdBy', 'updatedBy',
                          'createdDate', 'updatedDate', 'isDeleted']:
                if field in data:
                    setattr(student, field, data[field])

            student.save()
            return Response({
                "message": "Cập nhật học sinh thành công",
                "student": SoStudentsSerializer(student).data
            })
        except SoStudent.DoesNotExist:
            return Response({"error": "Không tìm thấy học sinh"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='ID học sinh cần xóa')
            },
            required=['id']
        ),
        responses={200: openapi.Response('Xoá mềm học sinh thành công')}
    )
    # @logger(level="log", name="delete_student")
    def delete(self, request, *args, **kwargs):
        try:
            student_id = request.data.get("id")
            if not student_id:
                return Response({"error": "Thiếu ID học sinh"}, status=400)
            student = SoStudent.objects.get(id=student_id)
            student.isDeleted = True
            student.save()
            return Response({"message": "Đã xoá học sinh."})
        except SoStudent.DoesNotExist:
            return Response({"error": "Không tìm thấy học sinh"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

