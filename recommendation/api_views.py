from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recommendation.fallback import recommend_with_fallback
from recommendation.models import RecommendationRequest
from recommendation.scoring import DIFFICULTY_FILTERS, SUNLIGHT_FILTERS
from recommendation.serializers import (
    RecommendationPlantsResponseSerializer,
    RecommendationRequestSerializer,
)


class RecommendationRequestViewSet(viewsets.ModelViewSet):
    """DRF ViewSet untuk CRUD permintaan rekomendasi dan hasil tanaman cocok."""

    serializer_class = RecommendationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RecommendationRequest.objects.filter(user=self.request.user)
        if self.action == "list":
            space_type = self.request.query_params.get("space_type", "")
            if space_type in dict(RecommendationRequest.SPACE_CHOICES):
                queryset = queryset.filter(space_type=space_type)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"], url_path="plants")
    def plants(self, request, pk=None):
        """Kembalikan daftar tanaman hasil scoring + status fallback Perenual."""
        recommendation = self.get_object()
        sunlight = request.query_params.get("sunlight", "")
        difficulty = request.query_params.get("difficulty", "")
        if sunlight not in SUNLIGHT_FILTERS:
            sunlight = ""
        if difficulty not in DIFFICULTY_FILTERS:
            difficulty = ""

        matches, lookup = recommend_with_fallback(
            request.user,
            recommendation,
            sunlight=sunlight,
            difficulty=difficulty,
        )
        serializer = RecommendationPlantsResponseSerializer(
            {
                "recommendation": recommendation,
                "plants": matches,
                "lookup": lookup,
            }
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="options",
        permission_classes=[permissions.AllowAny],
    )
    def options(self, request):
        """Pilihan form dan filter yang valid untuk dipakai aplikasi mobile."""
        return Response(
            {
                "space_type": [
                    {"value": value, "label": label}
                    for value, label in RecommendationRequest.SPACE_CHOICES
                ],
                "watering_frequency": [
                    {"value": value, "label": label}
                    for value, label in RecommendationRequest.WATERING_CHOICES
                ],
                "experience_level": [
                    {"value": value, "label": label}
                    for value, label in RecommendationRequest.EXPERIENCE_CHOICES
                ],
                "sunlight_filters": [
                    {"value": key, "label": label}
                    for key, (label, _) in SUNLIGHT_FILTERS.items()
                ],
                "difficulty_filters": [
                    {"value": key, "label": label}
                    for key, (label, _) in DIFFICULTY_FILTERS.items()
                ],
            }
        )
