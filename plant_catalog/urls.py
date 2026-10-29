from django.urls import path
from . import views

app_name = "plant_catalog"

urlpatterns = [
    path("", views.plant_catalog, name="catalog"),
    path("<uuid:plant_id>/", views.plant_detail, name="detail"),
]