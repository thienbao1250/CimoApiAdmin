from rest_framework import serializers
from Classes.models.SoClassUsers import SoClassUsers

class SoClassUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoClassUsers
        fields = ['id', 'soClassId', 'soUserId']
