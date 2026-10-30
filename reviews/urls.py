
from django.urls import path

from .views import add_plant_review, edit_plant_review, delete_plant_review

app_name = "reviews"

urlpatterns = [
    path(
        "plants/<uuid:plant_id>/review/",
        add_plant_review,
        name="plant_review",
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
]