from django.urls import path
from . import views

app_name = "plant_catalog"

urlpatterns = [
    path("", views.plant_catalog, name="catalog"),
    path("<uuid:plant_id>/", views.plant_detail, name="detail"),
    path("add/", views.add_plant, name="add"),
    path("<uuid:plant_id>/edit/", views.edit_plant, name="edit"),
    path("<uuid:plant_id>/delete/", views.delete_plant, name="delete"),
]