from Parents.models import SoStudentParents,SoParents
from Parents.serializers import SoStudentParentsSerializer,SoParentsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorator import logger

class SoParentsAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Lấy danh sách tất cả phụ huynh (isDeleted=False)",
        responses={200: SoParentsSerializer(many=True)}
    )
    @logger(level="log", name="get_parents")
    def get(self, request, *args, **kwargs):
        parents = SoParents.objects.filter(isDeleted=False)
        serializer = SoParentsSerializer(parents, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'dob': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'gender': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                'nationalId': openapi.Schema(type=openapi.TYPE_STRING),
                'relation': openapi.Schema(type=openapi.TYPE_STRING),
                'job': openapi.Schema(type=openapi.TYPE_STRING),
                'avt': openapi.Schema(type=openapi.TYPE_STRING),
                'studentIds': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Danh sách ID học sinh liên kết"
                ),
                'createdBy': openapi.Schema(type=openapi.TYPE_STRING),
                'updatedBy': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['name', 'studentIds']
        ),
        responses={201: SoParentsSerializer}
    )
    @logger(level="log", name="create_parent")
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            parent_id = str(uuid.uuid4())
            parent = SoParents.objects.create(
                id=parent_id,
                name=data.get("name"),
                dob=data.get("dob"),
                gender=data.get("gender"),
                phone=data.get("phone"),
                email=data.get("email"),
                address=data.get("address"),
                nationalId=data.get("nationalId"),
                relation=data.get("relation"),
                job=data.get("job"),
                avt=data.get("avt"),
                createdBy=data.get("createdBy"),
                updatedBy=data.get("updatedBy"),
            )
            student_ids = data.get("studentIds", [])
            for student_id in student_ids:
                SoStudentParents.objects.create(
                    id=str(uuid.uuid4()), 
                    soStudentid=student_id,
                    soParentid=parent_id,
                    isDeleted=False
            )
            return Response({
                "message": "Thêm phụ huynh thành công",
                "parent": SoParentsSerializer(parent).data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'dob': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'gender': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                'nationalId': openapi.Schema(type=openapi.TYPE_STRING),
                'relation': openapi.Schema(type=openapi.TYPE_STRING),
                'job': openapi.Schema(type=openapi.TYPE_STRING),
                'avt': openapi.Schema(type=openapi.TYPE_STRING),
                'studentIds': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Danh sách ID học sinh liên kết mới"
                ),
                'createdBy': openapi.Schema(type=openapi.TYPE_STRING),
                'updatedBy': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['id']
        ),
        responses={200: SoParentsSerializer}
    )
    @logger(level="log", name="update_parent")
    def patch(self, request, *args, **kwargs):
        try:
            data = request.data
            parent_id = data.get("id")
            parent = SoParents.objects.get(id=parent_id)

            for field in ['name', 'dob', 'gender', 'phone', 'email', 'address', 'nationalId', 'relation', 'job', 'avt', 'createdBy', 'updatedBy']:
                if field in data:
                    setattr(parent, field, data[field])
            parent.save()

            if "studentIds" in data:
                SoStudentParents.objects.filter(soParentid=parent_id).delete()
                for sid in data["studentIds"]:
                    SoStudentParents.objects.create(soStudentid=sid, soParentid=parent_id)

            return Response({
                "message": "Cập nhật phụ huynh thành công",
                "parent": SoParentsSerializer(parent).data
            })
        except SoParents.DoesNotExist:
            return Response({"error": "Không tìm thấy phụ huynh"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'id': openapi.Schema(type=openapi.TYPE_STRING)},
            required=['id']
        ),
        responses={200: openapi.Response('Xoá thành công')}
    )
    @logger(level="log", name="delete_parent")
    def delete(self, request, *args, **kwargs):
        try:
            parent_id = request.data.get("id")
            parent = SoParents.objects.get(id=parent_id)
            parent.isDeleted = True
            parent.save()
            return Response({"message": "Đã xoá phụ huynh (mềm)"})
        except SoParents.DoesNotExist:
            return Response({"error": "Không tìm thấy phụ huynh"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class SoStudentParentsAPI(APIView):

    @swagger_auto_schema(
        operation_description="Lấy danh sách tất cả liên kết học sinh - phụ huynh (isDeleted=False)",
        responses={200: SoStudentParentsSerializer(many=True)}
    )
    @logger(level="log", name="get_student_parents")
    def get(self, request):
        links = SoStudentParents.objects.filter(isDeleted=False)
        serializer = SoStudentParentsSerializer(links, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'soParentid': openapi.Schema(type=openapi.TYPE_STRING, description="ID phụ huynh"),
                'studentIds': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Danh sách ID học sinh liên kết"
                ),
                'createdBy': openapi.Schema(type=openapi.TYPE_STRING),
                'updatedBy': openapi.Schema(type=openapi.TYPE_STRING),
                'createdDate': openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                'updatedDate': openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
            },
            required=['soParentid', 'studentIds']
        ),
        responses={201: SoStudentParentsSerializer(many=True)}
    )
    @logger(level="log", name="create_student_parents")
    def post(self, request):
        try:
            data = request.data
            parent_id = data.get("soParentid")
            student_ids = data.get("studentIds", [])

            created_by = data.get("createdBy")
            updated_by = data.get("updatedBy")
            created_date = data.get("createdDate")
            updated_date = data.get("updatedDate")

            results = []
            for student_id in student_ids:
                link = SoStudentParents.objects.create(
                    id=str(uuid.uuid4()),
                    soStudentid=student_id,
                    soParentid=parent_id,
                    createdBy=created_by,
                    updatedBy=updated_by,
                    createdDate=created_date,
                    updatedDate=updated_date,
                    isDeleted=False
                )
                results.append(link)

            return Response({
                "message": f"Đã tạo {len(results)} liên kết thành công",
                "data": SoStudentParentsSerializer(results, many=True).data
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        request_body=SoStudentParentsSerializer,
        responses={200: SoStudentParentsSerializer}
    )
    @logger(level="log", name="update_student_parents")
    def patch(self, request):
        try:
            data = request.data
            link_id = data.get("id")
            if not link_id:
                return Response({"error": "Thiếu ID liên kết"}, status=400)

            link = SoStudentParents.objects.get(id=link_id)

            for field in ['soStudentid', 'soParentid', 'createdBy', 'updatedBy', 'createdDate', 'updatedDate', 'isDeleted']:
                if field in data:
                    setattr(link, field, data[field])

            link.save()
            return Response({
                "message": "Cập nhật liên kết thành công",
                "data": SoStudentParentsSerializer(link).data
            })
        except SoStudentParents.DoesNotExist:
            return Response({"error": "Không tìm thấy liên kết"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: openapi.Response('Xoá mềm thành công')}
    )
    @logger(level="log", name="delete_student_parents") 
    def delete(self, request, id=None):
        try:
            if not id:
                return Response({"error": "Thiếu ID"}, status=400)
            link = SoStudentParents.objects.get(id=id)
            link.isDeleted = True
            link.save()
            return Response({"message": "Đã xoá mềm liên kết"})
        except SoStudentParents.DoesNotExist:
            return Response({"error": "Không tìm thấy liên kết"}, status=404)
