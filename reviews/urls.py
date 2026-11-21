
from django.urls import path

from .views import add_plant_review, edit_plant_review, delete_plant_review
from .api_views import api_add_review, api_edit_or_delete_review

app_name = "reviews"

urlpatterns = [
    path(
        "plants/<int:plant_id>/review/",
        add_plant_review,
        name="plant_review"
    ),
    path(
        "reviews/<int:review_id>/edit/",
        edit_plant_review,
        name="edit_plant_review"
    ),
    path(
        "reviews/<int:review_id>/delete/",
        delete_plant_review,
        name="delete_plant_review"
    ),
    path(
        "api/plants/<uuid:plant_id>/reviews/", 
        api_add_review,
        name="api_add_review"
    ),
    path(
        "api/reviews/<int:review_id>/", 
        api_edit_or_delete_review,
        name="api_edit_or_delete_review"
    ),
]