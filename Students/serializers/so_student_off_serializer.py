# Parents/serializers/so_student_off_serializer.py
from rest_framework import serializers
from Students.models.SoStudentOff import SoStudentOff
from Students.serializers.so_students_serializer import SoStudentsSerializer
from Parents.serializers.so_parents_serializer import SoParentsSerializer
from Students.models.SoStudents import SoStudent
from Parents.models import SoParents
from Classes.models import SoClasses
from Classes.serializers.so_classes_serializer import SoClassesSerializer

class SoStudentOffSerializer(serializers.ModelSerializer):
    # student = serializers.SerializerMethodField()
    # parent = serializers.SerializerMethodField()

    class Meta:
        model = SoStudentOff
        fields = [
            'id', 'student_id',
            'parent_id',
            'leaveStartDate', 'leaveEndDate',
            'reason', 'note', 'leaveStatus',
            'createdDate', 'updatedDate', 'createdBy', 'updatedBy', 'class_id',
        ]

    def get_student(self, obj):
        try:
            # from Students.models import SoStudent
            student = SoStudent.objects.get(id=obj.student_id)
            # from Students.serializers.so_students_serializer import SoStudentsSerializer
            return SoStudentsSerializer(student).data
        except SoStudent.DoesNotExist:
            return None

    def get_parent(self, obj):
        try:
            # from Parents.models import SoParents
            parent = SoParents.objects.get(id=obj.parent_id)
            # from Parents.serializers.so_parents_serializer import SoParentsSerializer
            return SoParentsSerializer(parent).data
        except SoParents.DoesNotExist:
            return None
    def get_class(self, obj):
        try:
            # from Students.models import SoClasses
            class_instance = SoClasses.objects.get(id=obj.class_id)
            # from Students.serializers.so_classes_serializer import SoClassesSerializer
            return SoClassesSerializer(class_instance).data
        except SoClasses.DoesNotExist:
            return None
        
