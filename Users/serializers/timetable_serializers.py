# # serializers.py
# from rest_framework import serializers
# from Users.models.Timetables import Timetable
# from Users.models.souser import SoUser
# from Users.serializers.subject_serializer import SubjectSerializer
# from Users.serializers.so_user_serializer import SoUserSerializer
# from Users.models.subject import Subject

# class TimetableSerializer(serializers.ModelSerializer):
#     subject = SubjectSerializer(read_only = True)
#     subject_name = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(),source='subject.name',write_only = True)
#     user = serializers.StringRelatedField(source='soUser.name')  # Lấy tên giáo viên
#     classroom = serializers.StringRelatedField(source='class_id.name')  # Lấy tên phòng học

#     class Meta:
#         model = Timetable
#         fields = ['id', 'subject','subject_name', 'user', 'classroom', 'date', 'start_time', 'end_time']


# serializers.py
from rest_framework import serializers
from Users.models.Timetables import Timetable
from Users.models.subject import Subject
from Users.models.souser import SoUser
from Classes.models.SoClasses import SoClasses
from Users.serializers.subject_serializer import SubjectSerializer
from Users.serializers.so_user_serializer import SoUserSerializer
from Classes.serializers.so_classes_serializer import SoClassesSerializer

class TimetableSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)  # Trả về thông tin chi tiết của môn học
    subject_name = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), source='subject', write_only=True)
    teacher = SoUserSerializer(read_only=True)   # Trả về thông tin chi tiết của giáo viên
    classroom = SoClassesSerializer(read_only=True)  # Trả về thông tin chi tiết của lớp học

    class Meta:
        model = Timetable
        fields = ['id', 'subject','subject_name', 'teacher', 'classroom', 'date', 'start_time', 'end_time']
