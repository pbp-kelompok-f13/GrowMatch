from django.urls import reverse
from rest_framework import serializers

from recommendation.models import RecommendationRequest
from recommendation.weather import LocationNotFound, apply_location_and_weather


class RecommendationRequestSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    city = serializers.ReadOnlyField()
    watering_label = serializers.ReadOnlyField()
    has_weather = serializers.ReadOnlyField()
    space_type_display = serializers.CharField(source="get_space_type_display", read_only=True)
    watering_frequency_display = serializers.CharField(
        source="get_watering_frequency_display",
        read_only=True,
    )
    experience_level_display = serializers.CharField(
        source="get_experience_level_display",
        read_only=True,
    )

    class Meta:
        model = RecommendationRequest
        fields = [
            "id",
            "user",
            "location_name",
            "city",
            "latitude",
            "longitude",
            "space_type",
            "space_type_display",
            "watering_frequency",
            "watering_frequency_display",
            "watering_label",
            "experience_level",
            "experience_level_display",
            "temperature",
            "humidity",
            "has_weather",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "latitude",
            "longitude",
            "temperature",
            "humidity",
            "created_at",
            "updated_at",
        ]

    def validate_location_name(self, value):
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError("Location must be at least 2 characters.")
        return cleaned

    def _populate_weather(self, instance):
        try:
            apply_location_and_weather(instance)
        except LocationNotFound:
            raise serializers.ValidationError(
                {"location_name": ["Location not found. Try another city name."]}
            )

    def create(self, validated_data):
        instance = RecommendationRequest(**validated_data)
        self._populate_weather(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        location_updated = "location_name" in validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if location_updated:
            self._populate_weather(instance)
        instance.save()
        return instance


class RecommendedPlantSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="plant.id", read_only=True)
    detail_url = serializers.SerializerMethodField()
    name = serializers.CharField(source="plant.name", read_only=True)
    scientific_name = serializers.CharField(source="plant.scientific_name", read_only=True)
    image_url = serializers.CharField(source="plant.image_url", read_only=True)
    indoor = serializers.BooleanField(source="plant.indoor", allow_null=True, read_only=True)
    sunlight = serializers.CharField(source="plant.sunlight", read_only=True)
    watering = serializers.CharField(source="plant.watering", read_only=True)
    difficulty = serializers.CharField(source="plant.difficulty", read_only=True)
    score = serializers.FloatField(read_only=True)
    match_percent = serializers.IntegerField(read_only=True)
    reasons = serializers.ListField(child=serializers.CharField(), read_only=True)

    def get_detail_url(self, obj):
        return reverse("plant_catalog:detail", args=[obj["plant"].id])


class PerenualLookupStatusSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    lookups_left = serializers.IntegerField()
    added = serializers.IntegerField()
    message = serializers.CharField(allow_blank=True)


class RecommendationPlantsResponseSerializer(serializers.Serializer):
    recommendation = RecommendationRequestSerializer()
    plants = RecommendedPlantSerializer(many=True)
    lookup = PerenualLookupStatusSerializer()
