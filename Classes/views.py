from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Classes.models.SoClasses import SoClasses
from Classes.serializers.so_classes_serializer import SoClassesSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
import json
from utils.decorator import logger

class SoClassesAPI(APIView):

    @swagger_auto_schema(
        operation_description="Lấy danh sách lớp học (isDeleted=False)",
        responses={200: SoClassesSerializer(many=True)}
    )
    # @logger(level="log", name="get_classes")
    def get(self, request,*args, **kwargs):
        classes = SoClasses.objects.filter(isDeleted=False)
        serializer = SoClassesSerializer(classes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SoClassesSerializer,
        responses={201: SoClassesSerializer}
    )
    # @logger(level="log", name="create_class")
    def post(self, request,*args, **kwargs):
        try:
            data = request.data
            new_class = SoClasses.objects.create(
                id=data.get('id') or str(uuid.uuid4()),
                name=data.get('name'),
                isDeleted=data.get("isDeleted", False),
                createdBy=data.get("createdBy"),
                updatedBy=data.get("updatedBy"),
                createdDate=data.get("createdDate"),
                updatedDate=data.get("updatedDate"),
            )
            return Response({
                "message": "Thêm lớp học thành công",
                "data": SoClassesSerializer(new_class).data
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=SoClassesSerializer,
        responses={200: SoClassesSerializer}
    )
    # @logger(level="log", name="update_class")
    def patch(self, request,class_id,*args, **kwargs):
        try:
            data = request.data
            # class_id = data.get("id")
            if not class_id:
                return Response({"error": "Thiếu ID lớp học"}, status=400)
            class_obj = SoClasses.objects.get(id=class_id)

            for field in ['name', 'isDeleted', 'createdBy', 'updatedBy', 'createdDate', 'updatedDate']:
                if field in data:
                    setattr(class_obj, field, data[field])
            class_obj.save()
            return Response({
                "message": "Cập nhật lớp học thành công",
                "data": SoClassesSerializer(class_obj).data
            })
        except SoClasses.DoesNotExist:
            return Response({"error": "Không tìm thấy lớp học"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='ID lớp học cần xoá')
            },
            required=['id']
        ),
        responses={200: openapi.Response("Xoá lớp học thành công")}
    )
    # @logger(level="log", name="delete_class")
    def delete(self, request,class_id,*args, **kwargs):
        try:
            # class_id = request.data.get("id")
            if not class_id:
                return Response({"error": "Thiếu ID lớp học"}, status=400)
            class_obj = SoClasses.objects.get(id=class_id)
            class_obj.isDeleted = True
            class_obj.save()
            return Response({"message": "Đã xoá lớp học."})
        except SoClasses.DoesNotExist:
            return Response({"error": "Không tìm thấy lớp học"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class SoClassesCountAPI(APIView):
    @swagger_auto_schema(
        operation_description="Đếm số lượng lớp học (có thể lọc bằng `where`)",
        manual_parameters=[
            openapi.Parameter('where', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Lọc theo điều kiện JSON')
        ],
        responses={200: openapi.Response("Số lượng lớp học", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ))}
    )
    # @logger(level="log", name="count_classes")
    def get(self, request,*args, **kwargs):
        queryset = SoClasses.objects.filter(isDeleted=False)
        where = request.query_params.get('where')
        if where:
            try:
                filters = json.loads(where)
                queryset = queryset.filter(**filters)
            except Exception as e:
                return Response({"error": "Lỗi định dạng where"}, status=400)

        return Response({"count": queryset.count()})