from rest_framework import serializers
from Role.models import SoRole

class SoRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoRole
        fields = '__all__'
