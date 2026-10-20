
from django.urls import path

from main.views import *

app_name = "main"

urlpatterns = [
    path("", show_main),
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
]