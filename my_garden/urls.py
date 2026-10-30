from django.urls import path
from . import views

app_name = "my_garden"

urlpatterns = [
    path("", views.my_garden_view, name="index"),
    path(
        "add/<uuid:plant_id>/",
        views.add_to_garden,
        name="add",
    ),
    path(
        "edit/<int:garden_plant_id>/",
        views.edit_garden_plant,
        name="edit",
    ),
    path(
        "remove/<int:garden_plant_id>/",
        views.remove_from_garden,
        name="remove",
    ),
]