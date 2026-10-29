from django.conf import settings
from django.db import models


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    location = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"