from django.apps import AppConfig


class MyGardenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "my_garden"
    verbose_name = "My Garden"