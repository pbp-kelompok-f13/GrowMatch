import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 5


class LocationNotFound(Exception):
    pass


def geocode(location_name):
    """Ubah nama kota jadi koordinat lewat Open-Meteo Geocoding API.

    Mengembalikan dict berisi name, latitude, longitude. Mengembalikan None
    kalau API tidak bisa dihubungi, dan raise LocationNotFound kalau kota
    tidak ditemukan.
    """
    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": location_name, "count": 1, "language": "id", "format": "json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    results = data.get("results") or []
    if not results:
        raise LocationNotFound(location_name)

    result = results[0]
    name = ", ".join(part for part in (result.get("name"), result.get("country")) if part)
    return {
        "name": name or location_name,
        "latitude": result["latitude"],
        "longitude": result["longitude"],
    }


def get_current_weather(latitude, longitude):
    """Ambil suhu (°C) dan kelembapan (%) saat ini. None kalau API gagal."""
    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        current = response.json()["current"]
        return {
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
        }
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


def apply_location_and_weather(recommendation):
    """Isi koordinat dan cuaca ke objek rekomendasi (belum di-save).

    Mengembalikan False kalau Open-Meteo tidak bisa dihubungi, supaya view
    bisa kasih tahu user. LocationNotFound diteruskan ke pemanggil.
    """
    location = geocode(recommendation.location_name)
    if location is None:
        recommendation.latitude = recommendation.longitude = None
        recommendation.temperature = recommendation.humidity = None
        return False

    recommendation.location_name = location["name"]
    recommendation.latitude = location["latitude"]
    recommendation.longitude = location["longitude"]

    weather = get_current_weather(location["latitude"], location["longitude"])
    if weather is None:
        recommendation.temperature = recommendation.humidity = None
        return False

    recommendation.temperature = weather["temperature"]
    recommendation.humidity = weather["humidity"]
    return True
