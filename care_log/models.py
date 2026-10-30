from django.conf import settings
from django.db import models

from my_garden.models import GardenPlant


class CareActivity(models.Model):
    class ActivityType(models.TextChoices):
        WATERING = "watering", "Penyiraman"
        FERTILIZING = "fertilizing", "Pemupukan"
        PRUNING = "pruning", "Pemangkasan"
        REPOTTING = "repotting", "Penggantian Pot"
        PEST_CONTROL = "pest_control", "Pengendalian Hama"
        OTHER = "other", "Lainnya"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="care_activities",
    )

    garden_plant = models.ForeignKey(
        GardenPlant,
        on_delete=models.CASCADE,
        related_name="care_activities",
    )

    activity_type = models.CharField(
        max_length=30,
        choices=ActivityType.choices,
    )

    activity_date = models.DateTimeField()

    notes = models.TextField(
        blank=True,
        help_text="Detail aktivitas perawatan.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]

    def __str__(self):
        return (
            f"{self.get_activity_type_display()} - "
            f"{self.garden_plant.plant.name}"
        )