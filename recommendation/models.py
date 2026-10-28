import uuid

from django.contrib.auth.models import User
from django.db import models


class RecommendationRequest(models.Model):
    SPACE_CHOICES = [
        ("indoor", "Indoor"),
        ("outdoor", "Outdoor"),
    ]
    # Nilai disamakan dengan field "watering" di Perenual API
    WATERING_CHOICES = [
        ("frequent", "Often (almost every day)"),
        ("average", "Sometimes (2-3 times a week)"),
        ("minimum", "Rarely (once a week or less)"),
    ]
    EXPERIENCE_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Experienced"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recommendation_requests",
    )
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    space_type = models.CharField(max_length=10, choices=SPACE_CHOICES)
    watering_frequency = models.CharField(max_length=10, choices=WATERING_CHOICES)
    experience_level = models.CharField(max_length=15, choices=EXPERIENCE_CHOICES)

    # Kondisi lingkungan dari Open-Meteo saat rekomendasi dibuat/diubah
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.location_name} ({self.get_space_type_display()})"

    @property
    def has_weather(self):
        return self.temperature is not None and self.humidity is not None

    def to_dict(self):
        return {
            "id": str(self.id),
            "user": self.user.username,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "space_type": self.space_type,
            "watering_frequency": self.watering_frequency,
            "experience_level": self.experience_level,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
