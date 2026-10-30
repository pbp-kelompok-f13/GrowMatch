import uuid

from django.db import models
from django.db.models import Avg

from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from django.contrib.auth.models import User

# Create your models here.

class HomepagePlant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    latin = models.CharField(max_length=255)
    image = models.CharField(max_length=255)

class PlantReview(models.Model):
    plant = models.ForeignKey(
        "plant_catalog.Plant",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

