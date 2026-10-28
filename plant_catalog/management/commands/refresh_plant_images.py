import os
import requests

from django.core.management.base import BaseCommand

from plant_catalog.models import Plant


class Command(BaseCommand):
    help = "Refresh expired plant image URLs"

    def handle(self, *args, **options):
        api_key = os.getenv("PERENUAL_API_KEY")

        if not api_key:
            self.stderr.write("PERENUAL_API_KEY tidak ditemukan.")
            return

        plants = Plant.objects.exclude(perenual_id=None)

        for plant in plants:
            response = requests.get(
                f"https://perenual.com/api/v2/species/details/{plant.perenual_id}",
                params={"key": api_key},
                timeout=20,
            )

            response.raise_for_status()
            data = response.json()

            default_image = data.get("default_image") or {}
            new_image_url = default_image.get("regular_url") or default_image.get("original_url") or ""

            if new_image_url:
                plant.image_url = new_image_url
                plant.save(update_fields=["image_url"])
                self.stdout.write(self.style.SUCCESS(f"Updated: {plant.name}"))
            else:
                self.stdout.write(f"No image: {plant.name}")