import uuid

from django.db import models

# Create your models here.

class HomepagePlant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    latin = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    

