from django.db import models
from Users.models.base import BaseModel
import uuid

class SoRole(BaseModel):
    id = models.CharField(primary_key=True, max_length=512)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'sorole'

    def __str__(self):
        return self.name
