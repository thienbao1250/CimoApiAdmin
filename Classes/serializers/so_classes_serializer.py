from rest_framework import serializers
from Classes.models.SoClasses import SoClasses

class SoClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoClasses
        fields = ['id', 'name']
