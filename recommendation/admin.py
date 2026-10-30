from django.contrib import admin

from recommendation.models import PerenualLookup, RecommendationRequest


@admin.register(RecommendationRequest)
class RecommendationRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "location_name", "space_type", "watering_frequency", "experience_level", "created_at")
    list_filter = ("space_type", "watering_frequency", "experience_level")
    search_fields = ("user__username", "location_name")


@admin.register(PerenualLookup)
class PerenualLookupAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "success", "plants_added")
    list_filter = ("success",)
