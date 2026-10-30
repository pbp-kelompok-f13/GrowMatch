from django.contrib import admin
from .models import CareActivity


@admin.register(CareActivity)
class CareActivityAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "garden_plant",
        "activity_type",
        "activity_date",
    )

    list_filter = ("activity_type", "activity_date")

    search_fields = (
        "user__username",
        "garden_plant__plant__name",
        "notes",
    )