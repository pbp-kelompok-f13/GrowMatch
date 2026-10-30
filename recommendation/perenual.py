import os

import requests

from plant_catalog.models import Plant

LIST_URL = "https://perenual.com/api/v2/species-list"
DETAIL_URL = "https://perenual.com/api/v2/species/details/{id}"
TIMEOUT = 10
# Paket gratis Perenual cuma bisa ambil detail buat ID 1-3000
FREE_PLAN_MAX_ID = 3000
LIMIT_STATUS_CODES = (401, 402, 403, 429)

# Filter cahaya di halaman hasil -> nilai parameter sunlight Perenual
SUNLIGHT_PARAMS = {
    "full_sun": "full_sun",
    "part_shade": "part_shade",
    "shade": "full_shade",
}


class PerenualError(Exception):
    pass


class PerenualLimitReached(PerenualError):
    pass


def get_api_key():
    return os.getenv("PERENUAL_API_KEY", "").strip()


def _get(url, params):
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.RequestException as error:
        raise PerenualError(str(error)) from error

    if response.status_code in LIMIT_STATUS_CODES:
        raise PerenualLimitReached(f"HTTP {response.status_code}")
    try:
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        raise PerenualError(str(error)) from error


def search_species_ids(api_key, recommendation, sunlight=""):
    params = {"key": api_key, "watering": recommendation.watering_frequency}
    if recommendation.space_type == "indoor":
        params["indoor"] = 1
    if sunlight in SUNLIGHT_PARAMS:
        params["sunlight"] = SUNLIGHT_PARAMS[sunlight]

    data = _get(LIST_URL, params)
    items = data.get("data") if isinstance(data, dict) else None
    return [item["id"] for item in items or [] if isinstance(item, dict) and isinstance(item.get("id"), int)]


def _clean(value):
    # Field premium Perenual isinya teks "Upgrade Plans To Premium..."
    if isinstance(value, str) and value.lower().startswith("upgrade"):
        return ""
    return value


def _join(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if not str(item).lower().startswith("upgrade"))
    return _clean(value) or ""


def plant_defaults(data):
    """Mapping detail Perenual ke field Plant, sama kayak command import_plants."""
    scientific_name = _join(data.get("scientific_name"))
    name = _clean(data.get("common_name")) or scientific_name
    if not name:
        return None

    image = data.get("default_image") or {}
    benchmark = data.get("watering_general_benchmark") or {}
    interval = ""
    if isinstance(benchmark, dict):
        value = str(benchmark.get("value") or "").strip('"')
        interval = f"{value} {benchmark.get('unit') or ''}".strip() if value else ""

    def as_list(key):
        value = data.get(key)
        return value if isinstance(value, list) else []

    return {
        "name": name,
        "scientific_name": scientific_name,
        "description": _clean(data.get("description")) or "",
        "image_url": (image.get("regular_url") if isinstance(image, dict) else "") or "",
        "indoor": data.get("indoor") if isinstance(data.get("indoor"), bool) else None,
        "sunlight": _join(data.get("sunlight")),
        "watering": _clean(data.get("watering")) or "",
        "watering_interval": interval,
        "difficulty": _clean(data.get("care_level")) or "",
        "soil": as_list("soil"),
        "propagation": as_list("propagation"),
        "pruning_month": as_list("pruning_month"),
        "growth_rate": _clean(data.get("growth_rate")) or "",
        "maintenance": _clean(data.get("maintenance")) or "",
    }


def fetch_new_plants(api_key, recommendation, sunlight="", limit=2):
    """Cari tanaman baru di Perenual dan simpan ke tabel Plant.

    Total request: 1 list + maksimal `limit` detail. Raise PerenualError kalau
    pencarian awal gagal; kegagalan di detail cuma melewatkan tanaman itu.
    """
    ids = search_species_ids(api_key, recommendation, sunlight)
    existing = set(Plant.objects.filter(perenual_id__in=ids).values_list("perenual_id", flat=True))
    candidates = [plant_id for plant_id in ids if 0 < plant_id <= FREE_PLAN_MAX_ID and plant_id not in existing]

    plants = []
    for plant_id in candidates[:limit]:
        try:
            data = _get(DETAIL_URL.format(id=plant_id), {"key": api_key})
        except PerenualLimitReached:
            break
        except PerenualError:
            continue
        defaults = plant_defaults(data) if isinstance(data, dict) else None
        if defaults:
            plant, _ = Plant.objects.update_or_create(perenual_id=plant_id, defaults=defaults)
            plants.append(plant)
    return plants
