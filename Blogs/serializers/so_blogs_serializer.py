from rest_framework import serializers
from Blogs.models import SoBlogs
import json

class SoBlogsSerializer(serializers.ModelSerializer):
    soClassId = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    
    class Meta:
        model = SoBlogs
        fields = [
            'id', 'name', 'sumary', 'imgs', 'description', 'category',
            'relateIds', 'soClassId', 'isDeleted', 'createdBy', 'updatedBy', 'createdDate', 'updatedDate'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['soClassId'] = json.loads(instance.soClassId or "[]")
        except:
            data['soClassId'] = []
        return data

    def create(self, validated_data):
        class_ids = validated_data.pop('soClassId', [])
        validated_data['soClassId'] = json.dumps(class_ids)
        return SoBlogs.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'soClassId' in validated_data:
            validated_data['soClassId'] = json.dumps(validated_data['soClassId'])
        return super().update(instance, validated_data)
