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
import pandas as pd
from Parents.models.SoParents import SoParents
from django.http import HttpResponse
from .models.HocKy import HocKy
from .models.Diem import Diem
from unidecode import unidecode

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
    def patch(self, request,user_id, *args, **kwargs):
        try:
            data = request.data
            # user_id = data.get("id")
            if not user_id:
                return Response({"error": "Thiếu ID người dùng"}, status=400)
            user = SoUser.objects.get(id=user_id)

            for field in ['username', 'name', 'dob', 'phone', 
                'email', 'address', 'nationalId', 'avt', 'createdBy', 'updatedBy']:
                if field in data:
                    setattr(user, field, data[field])
            if 'password' in data:
                user.password = make_password(data['password'])
            if 'roles' in data:
                user.soRoleIds = json.dumps(data['roles'])
                print(user.soRoleIds)

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
    def delete(self, request,user_id, *args, **kwargs):
        try:
            # user_id = request.data.get("id")
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



class ImportExcelAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Nhập dữ liệu từ file Excel",
        responses={200: openapi.Response('Dữ liệu đã được nhập thành công')}
    )
    def post(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file')
            import_type = request.POST.get('type', None) # truyền ?type=student|parent|user

            if not file:
                return Response({"error": "Không có file để nhập"}, status=400)
            if file.name == '':
                return Response({"error": "Tên file không hợp lệ"}, status=400)
            if not import_type:
                return Response({"error": "Thiếu loại dữ liệu import"}, status=400)

            if import_type == 'student':
                result = self.import_student(file)
                for item in result:
                    class_id = SoClasses.objects.filter(name= item.get("class")).first()
                    if class_id:
                        item['class'] = class_id.id
                        print(item['class'])
                    SoStudent.objects.create(
                        id=str(uuid.uuid4()),
                        name=item.get("name"),
                        soClassId=item.get("class"),
                        gender=item.get("gender"),
                        dob=item.get("dob"),
                        address=item.get("address"),
                        phone='0'+item.get("phone"),
                        email=item.get("email"),
                        createdBy= 'admin',  # Hoặc lấy từ request.user nếu có
                        updatedBy='admin',
                        isDeleted= item.get("isDeleted", False),
                        nationalId=item.get("nationalId", ""),
                        createdDate=datetime.now(),
                        updatedDate=datetime.now()
                        
                    )
            elif import_type == 'parent':
                result = self.import_parent(file)
                for item in result:
                    phone = '0'+str(item.get("phone_student"))
                    student_id = SoStudent.objects.filter(phone=phone).first()
                    if student_id:
                        item['student'] = student_id.id
                    parent= SoParents.objects.create(
                        id=str(uuid.uuid4()),
                        # soStudentId=item.get("student"),
                        name=item.get("name"),
                        phone=item.get("phone"),
                        email=item.get("email"),
                        address=item.get("address"),
                        relation=item.get("relation"),
                        dob = item.get("dob"),
                        gender =item.get("gender"),
                        job=item.get("job"),
                        nationalId=item.get("nationalId", ""),
                        createdBy='admin',  # Hoặc lấy từ request.user nếu có
                        updatedBy='admin',
                        isDeleted=item.get("isDeleted", False),
                        createdDate=datetime.now(),
                        updatedDate=datetime.now()
                    )
                    print(item.get('student'))
                    print(parent.id)
                    SoStudentParents.objects.create(
                        id=str(uuid.uuid4()),
                        soStudentid=item.get('student'),
                        soParentid=parent.id,
                        createdBy='admin',
                        updatedBy='admin',
                        createdDate=datetime.now(),
                        updatedDate=datetime.now()
                    )
            else:
                return Response({"error": "Loại dữ liệu import không hợp lệ"}, status=400)
            
            # Xử lý thêm nếu cần insert vào DB ở đây...
            # Sau đó trả về kết quả:
            return Response({"message": "Dữ liệu đã được nhập thành công", "data": result}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def import_student(self, file):
        df = pd.read_excel (file)
        # df.rename(columns={"Họ và tên": "ho_va_ten", "Lớp": "lop"}, inplace=True)
        return df.to_dict(orient="records")

    def import_parent(self, file):
        df = pd.read_excel (file)
        # Tùy chỉnh lại mapping column nếu cần
        return df.to_dict(orient="records")


class export_excel(APIView):
    @swagger_auto_schema(
        operation_description="Xuất dữ liệu người dùng ra file Excel",
        responses={200: openapi.Response('Dữ liệu đã được xuất thành công')}
    )
    def get(self, request, *args, **kwargs):
        class_id = request.GET.get('class_id')
        hoc_ky = request.GET.get('hoc_ky')
        name_hoc = request.GET.get('name_hoc')

        if not class_id:
            return Response({"error": "Thiếu ID lớp học"}, status=400)

        students = SoStudent.objects.filter(soClassId=class_id, isDeleted=False)
        hoc_ky_now = HocKy.objects.filter(ten_hoc_ky=hoc_ky, nam_hoc=name_hoc).first()
        if not hoc_ky_now:
            return Response({"error": "Không tìm thấy học kỳ"}, status=404)

        data = []
        for student in students:
            diem_obj = Diem.objects.filter(soStudentId=student.id, hoc_ky_id=hoc_ky_now.id).first()
            data.append({
                "name": student.name,
                "diem_15p": diem_obj.diem_15p if diem_obj else None,
                "diem_1tiet": diem_obj.diem_1tiet if diem_obj else None,
                "diem_mieng": diem_obj.diem_mieng if diem_obj else None,
                "diem_hk": diem_obj.diem_hk if diem_obj else None,
                "diem_tb": diem_obj.diem_tb if diem_obj else None,
            })

        df = pd.DataFrame(data)
        class_name = SoClasses.objects.filter(id=class_id).first()
        formatted_class_name = unidecode(class_name.name).replace(" ", "_") if class_name else "unknown_class"
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Diem_{formatted_class_name}.xlsx'
        # print(f"filename=diem_class_{formatted_class_name}")
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Diem')

        return response
