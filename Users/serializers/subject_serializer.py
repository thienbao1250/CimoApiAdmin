# serializers.py
from rest_framework import serializers
from Users.models.subject import Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description']  # Các trường cần thiết trong model Subject
