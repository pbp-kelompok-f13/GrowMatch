
import os
import requests

from django.core.management.base import BaseCommand, CommandError
from plant_catalog.models import Plant


class Command(BaseCommand):
    help = "Import selected plants from Perenual API"

    def add_arguments(self, parser):
        parser.add_argument("ids", nargs="+", type=int, help="Perenual species IDs")

    def handle(self, *args, **options):
        api_key = os.getenv("PERENUAL_API_KEY")
        if not api_key:
            raise CommandError("PERENUAL_API_KEY belum tersedia di .env")

        ids = list(dict.fromkeys(options["ids"]))

        if any(plant_id < 1 or plant_id > 3000 for plant_id in ids):
            raise CommandError("Free Plan hanya mendukung detail species ID 1-3000")

        for plant_id in ids:
            try:
                response = requests.get(
                    f"https://perenual.com/api/v2/species/details/{plant_id}",
                    params={"key": api_key},
                    timeout=20,
                )
                response.raise_for_status()
                data = response.json()

                image = data.get("default_image") or {}
                benchmark = data.get("watering_general_benchmark") or {}

                scientific_name = data.get("scientific_name") or []
                sunlight = data.get("sunlight") or []

                if isinstance(scientific_name, list):
                    scientific_name = ", ".join(scientific_name)

                if isinstance(sunlight, list):
                    sunlight = ", ".join(sunlight)

                interval = ""
                if isinstance(benchmark, dict):
                    value = str(benchmark.get("value") or "").strip('"')
                    unit = benchmark.get("unit") or ""
                    interval = f"{value} {unit}".strip() if value else ""

                name = data.get("common_name") or scientific_name
                if not name:
                    self.stdout.write(self.style.WARNING(f"Skip ID {plant_id}: nama kosong"))
                    continue

                Plant.objects.update_or_create(
                    perenual_id=plant_id,
                    defaults={
                        "name": name,
                        "scientific_name": scientific_name,
                        "description": data.get("description") or "",
                        "image_url": image.get("regular_url") or "",
                        "indoor": data.get("indoor"),
                        "sunlight": sunlight,
                        "watering": data.get("watering") or "",
                        "watering_interval": interval,
                        "difficulty": data.get("care_level") or "",
                        "soil": data.get("soil") or [],
                        "propagation": data.get("propagation") or [],
                        "pruning_month": data.get("pruning_month") or [],
                        "growth_rate": data.get("growth_rate") or "",
                        "maintenance": data.get("maintenance") or "",
                    },
                )

                self.stdout.write(self.style.SUCCESS(f"Imported: {name} (ID {plant_id})"))

            except requests.RequestException as error:
                self.stdout.write(self.style.ERROR(f"Failed ID {plant_id}: {error}"))
                if getattr(error.response, "status_code", None) == 429:
                    self.stdout.write("API limit reached. Stopping import.")
                    break
