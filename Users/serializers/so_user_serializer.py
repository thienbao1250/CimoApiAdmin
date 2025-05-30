from rest_framework import serializers
from Users.models import SoUser
from Role.models import SoRole   
from django.contrib.auth.hashers import make_password
from Role.serializers.so_role_serializer import SoRoleSerializer
import json

class SoUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name_roles = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    soRoleIds = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = SoUser
        fields = [
            'id', 'username', 'password', 'name', 'dob', 'phone', 'email',
            'address', 'nationalId', 'avt', 'soRoleIds', 'name_roles', 'roles'
        ]

    def get_name_roles(self, obj):
        role_ids = self._parse_roles(obj.soRoleIds)
        return ", ".join([
            SoRole.objects.filter(id=rid).first().name if SoRole.objects.filter(id=rid).exists() else "Không xác định"
            for rid in role_ids
        ])

    def get_roles(self, obj):
        role_ids = self._parse_roles(obj.soRoleIds)
        roles = SoRole.objects.filter(id__in=role_ids)
        return SoRoleSerializer(roles, many=True).data

    def _parse_roles(self, raw):
        try:
            if isinstance(raw, str):
                parsed = json.loads(raw)
                return parsed if isinstance(parsed, list) else [parsed]
            elif isinstance(raw, list):
                return raw
        except:
            return []
        return []

    def create(self, validated_data):
        roles = validated_data.get('soRoleIds', [])
        validated_data['soRoleIds'] = json.dumps(roles)
        validated_data['password'] = make_password(validated_data['password'])
        return SoUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        roles = validated_data.get('soRoleIds', [])
        validated_data['soRoleIds'] = json.dumps(roles)
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)