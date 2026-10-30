from django.conf import settings
from django.db import models
from plant_catalog.models import Plant


class GardenPlant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="garden_plants",
    )

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name="garden_entries",
    )

    nickname = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nama panggilan tanaman di kebun pribadi.",
    )

    date_added = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(
        blank=True,
        help_text="Catatan tentang tanaman.",
    )

    class Meta:
        ordering = ["-date_added"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "plant"],
                name="unique_user_garden_plant",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.plant.name}"