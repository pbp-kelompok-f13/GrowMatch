import uuid
from django.db import models


class Plant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    perenual_id = models.PositiveIntegerField(unique=True, null=True, blank=True)

    name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=1000, blank=True)
    image_attribution = models.TextField(blank=True)

    indoor = models.BooleanField(null=True, blank=True)
    sunlight = models.CharField(max_length=255, blank=True)
    watering = models.CharField(max_length=100, blank=True)
    watering_interval = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=100, blank=True)

    soil = models.JSONField(default=list, blank=True)
    propagation = models.JSONField(default=list, blank=True)
    pruning_month = models.JSONField(default=list, blank=True)
    growth_rate = models.CharField(max_length=100, blank=True)
    maintenance = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name