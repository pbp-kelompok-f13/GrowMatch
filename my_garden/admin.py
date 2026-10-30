from django.contrib import admin
from .models import GardenPlant


@admin.register(GardenPlant)
class GardenPlantAdmin(admin.ModelAdmin):
    list_display = ("user", "plant", "nickname", "date_added")
    list_filter = ("date_added",)
    search_fields = (
        "user__username",
        "plant__name",
        "nickname",
    )