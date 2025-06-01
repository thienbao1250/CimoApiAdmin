from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from Blogs.models import SoBlogs
from Blogs.serializers.so_blogs_serializer import SoBlogsSerializer
import uuid
import json
from utils.decorator import logger

class SoBlogsAPI(APIView):

    @swagger_auto_schema(
        operation_description="Lấy danh sách blogs (lọc theo lớp nếu cần)",
        manual_parameters=[
            openapi.Parameter('classId', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Lọc theo lớp (classId)")
        ],
        responses={200: SoBlogsSerializer(many=True)}
    )
    # @logger(level="log", name="get_blogs")
    def get(self, request,*args, **kwargs):
        class_id = request.query_params.get("classId")
        blogs = SoBlogs.objects.filter(isDeleted=False)
        if class_id:
            blogs = [b for b in blogs if class_id in json.loads(b.soClassId or "[]") or b.soClassId in [None, "", "[]"]]
        serializer = SoBlogsSerializer(blogs, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SoBlogsSerializer,
        responses={201: SoBlogsSerializer}
    )
    # @logger(level="log", name="create_blog")
    def post(self, request,*args, **kwargs):
        serializer = SoBlogsSerializer(data=request.data)
        if serializer.is_valid():
            blog = serializer.save(id=str(uuid.uuid4()))
            return Response({"message": "Tạo blog thành công", "data": SoBlogsSerializer(blog).data}, status=201)
        return Response({"error": serializer.errors}, status=400)

    @swagger_auto_schema(
        request_body=SoBlogsSerializer,
        responses={200: SoBlogsSerializer}
    )
    # @logger(level="log", name="update_blog")
    def patch(self, request,*args,blog_id, **kwargs):
        # blog_id = request.data.get("id")
        if not blog_id:
            return Response({"error": "Thiếu ID blog"}, status=400)
        try:
            blog = SoBlogs.objects.get(id=blog_id)
        except SoBlogs.DoesNotExist:
            return Response({"error": "Không tìm thấy blog"}, status=404)

        serializer = SoBlogsSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cập nhật blog thành công", "data": serializer.data})
        return Response({"error": serializer.errors}, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: openapi.Response("Xoá mềm blog thành công")}
    )
    # @logger(level="log", name="delete_blog")
    def delete(self, request,blog_id, *args, **kwargs):
        try:
            # blog_id = request.data.get("id")
            if not blog_id:
                return Response({"error": "Thiếu ID blog"}, status=400)

            blog = SoBlogs.objects.get(id=blog_id)
            blog.isDeleted = True
            blog.save()

            return Response({"message": "Đã xoá blog (mềm)"})
        except SoBlogs.DoesNotExist:
            return Response({"error": "Không tìm thấy blog"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
