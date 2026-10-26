from django.urls import path

from recommendation.views import (
    create_recommendation,
    delete_recommendation,
    edit_recommendation,
    show_detail,
    show_history,
    show_json,
    show_json_by_id,
    show_recommendation_form,
)

app_name = "recommendation"

urlpatterns = [
    path("", show_recommendation_form, name="form"),
    path("create/", create_recommendation, name="create"),
    path("history/", show_history, name="history"),
    path("json/", show_json, name="json"),
    path("json/<uuid:pk>/", show_json_by_id, name="json_by_id"),
    path("<uuid:pk>/", show_detail, name="detail"),
    path("<uuid:pk>/edit/", edit_recommendation, name="edit"),
    path("<uuid:pk>/delete/", delete_recommendation, name="delete"),
]
