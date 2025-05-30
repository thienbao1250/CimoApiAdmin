from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Role.models import SoRole
from Role.serializers.so_role_serializer import SoRoleSerializer
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
import json
from utils.decorator import logger

class SoRoleAPI(APIView):

    @swagger_auto_schema(
        operation_description="Lấy danh sách role (có thể lọc bằng where)",
        manual_parameters=[
            openapi.Parameter('where', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Lọc theo điều kiện JSON')
        ],
        responses={200: SoRoleSerializer(many=True)}
    )
    @logger(level="log", name="get_role")
    def get(self, request, *args, **kwargs):
        where = request.query_params.get("where")
        queryset = SoRole.objects.all()

        if where:
            try:
                filters = json.loads(where)
                queryset = queryset.filter(**filters)
            except Exception:
                return Response({"error": "Lỗi định dạng where"}, status=400)

        serializer = SoRoleSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SoRoleSerializer,
        responses={201: SoRoleSerializer}
    )
    @logger(level="log", name="create_role")
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            new_role = SoRole.objects.create(
                id=data.get("id") or str(uuid.uuid4()),
                name=data.get("name"),
                createdBy=data.get("createdBy"),
                updatedBy=data.get("updatedBy"),
                createdDate=data.get("createdDate"),
                updatedDate=data.get("updatedDate"),
            )
            return Response({
                "message": "Thêm role thành công",
                "data": SoRoleSerializer(new_role).data
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=SoRoleSerializer,
        responses={200: SoRoleSerializer}
    )
    @logger(level="log", name="update_role")
    def patch(self, request, *args, **kwargs):
        try:
            data = request.data
            role_id = data.get("id")
            if not role_id:
                return Response({"error": "Thiếu ID role"}, status=400)

            role = SoRole.objects.get(id=role_id)

            for field in ['name', 'createdBy', 'updatedBy', 'createdDate', 'updatedDate']:
                if field in data:
                    setattr(role, field, data[field])

            role.save()
            return Response({
                "message": "Cập nhật role thành công",
                "data": SoRoleSerializer(role).data
            })
        except SoRole.DoesNotExist:
            return Response({"error": "Không tìm thấy role"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='ID role cần xoá')
            },
            required=['id']
        ),
        responses={200: openapi.Response("Xoá role thành công")}
    )
    @logger(level="log", name="delete_role")
    def delete(self, request, *args, **kwargs):
        try:
            role_id = request.data.get("id")
            if not role_id:
                return Response({"error": "Thiếu ID role"}, status=400)

            role = SoRole.objects.get(id=role_id)
            role.delete()
            return Response({"message": "Đã xoá role"})
        except SoRole.DoesNotExist:
            return Response({"error": "Không tìm thấy role"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class SoRoleCountAPI(APIView):
    @swagger_auto_schema(
        operation_description="Đếm số lượng role (có thể lọc bằng where)",
        manual_parameters=[
            openapi.Parameter('where', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Điều kiện lọc JSON")
        ],
        responses={200: openapi.Response("Số lượng role", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ))}
    )
    @logger(level="log", name="count_role")
    def get(self, request, *args, **kwargs):
        queryset = SoRole.objects.all()
        where = request.query_params.get("where")

        if where:
            try:
                filters = json.loads(where)
                queryset = queryset.filter(**filters)
            except:
                return Response({"error": "Lỗi định dạng where"}, status=400)

        return Response({"count": queryset.count()})
