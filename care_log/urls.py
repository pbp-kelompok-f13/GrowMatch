from django.urls import path
from . import views

app_name = "care_log"

urlpatterns = [
    path("", views.care_log_view, name="index"),
    path("add/", views.add_activity, name="add"),
    path(
        "edit/<int:activity_id>/",
        views.edit_activity,
        name="edit",
    ),
    path(
        "delete/<int:activity_id>/",
        views.delete_activity,
        name="delete",
    ),
]