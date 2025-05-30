from django.db import models
from Users.models.base import BaseModel

class SoBlogs(BaseModel):
    name = models.CharField(max_length=255)
    sumary = models.TextField(null=True, blank=True)
    imgs = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    relateIds = models.CharField(max_length=255, null=True, blank=True)
    soClassId = models.CharField(max_length=512, db_column='soClassId') 
    
    class Meta:
        managed = False
        db_table = 'soblogs'
    def __str__(self):
        return self.name
