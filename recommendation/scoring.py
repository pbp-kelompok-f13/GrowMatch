from django.db.models import Q

from plant_catalog.models import Plant

MAX_SCORE = 10
DEFAULT_LIMIT = 12

# Urutan kebutuhan air; "none" dari Perenual dianggap sama dengan minimum
WATERING_LEVEL = {"minimum": 1, "none": 1, "average": 2, "frequent": 3}

# Poin pengalaman user terhadap tingkat kesulitan tanaman (care_level Perenual)
EXPERIENCE_POINTS = {
    "beginner": {"low": 3, "medium": 1.5, "moderate": 1.5, "high": 0},
    "intermediate": {"low": 3, "medium": 3, "moderate": 3, "high": 1.5},
    "expert": {"low": 3, "medium": 3, "moderate": 3, "high": 3},
}

SUNLIGHT_FILTERS = {
    "full_sun": ("Full sun", "full sun"),
    "part_shade": ("Part shade", "part"),
    "shade": ("Teduh", "shade"),
}
DIFFICULTY_FILTERS = {
    "low": ("Mudah", ("low",)),
    "medium": ("Sedang", ("medium", "moderate")),
    "high": ("Sulit", ("high",)),
}

HOT_TEMPERATURE = 24


def normalize(value):
    return (value or "").strip().lower()


def watering_points(recommendation, plant):
    plant_level = WATERING_LEVEL.get(normalize(plant.watering))
    if plant_level is None:
        return 1.5, None
    diff = abs(WATERING_LEVEL[recommendation.watering_frequency] - plant_level)
    points = {0: 3, 1: 1.5}.get(diff, 0)
    reason = "Kebutuhan airnya pas sama jadwal siram kamu" if diff == 0 else None
    return points, reason


def space_points(recommendation, plant):
    if recommendation.space_type == "indoor":
        points = {True: 3, None: 1, False: 0}[plant.indoor]
        reason = "Bisa tumbuh di dalam ruangan" if plant.indoor else None
    else:
        points = {False: 3, None: 2, True: 1}[plant.indoor]
        reason = "Cocok ditanam di luar ruangan" if plant.indoor is False else None
    return points, reason


def experience_points(recommendation, plant):
    difficulty = normalize(plant.difficulty)
    points = EXPERIENCE_POINTS[recommendation.experience_level].get(difficulty, 1.5)
    reason = None
    if difficulty == "low":
        reason = "Perawatannya mudah"
    elif points == 3 and difficulty:
        reason = "Sesuai sama pengalaman kamu"
    return points, reason


def weather_points(recommendation, plant):
    sunlight = normalize(plant.sunlight)
    if recommendation.space_type == "indoor":
        if "shade" in sunlight or "filtered" in sunlight:
            return 1, "Tahan cahaya redup dalam ruangan"
        return 0, None
    if recommendation.temperature is not None and recommendation.temperature >= HOT_TEMPERATURE:
        if "full sun" in sunlight:
            return 1, f"Kuat di cuaca panas ({recommendation.temperature:g}°C)"
    return 0, None


def score_plant(recommendation, plant):
    score, reason = space_points(recommendation, plant)
    if score == 0:
        # Tanaman khusus outdoor nggak direkomendasiin buat ruang indoor
        return 0, []

    reasons = [reason] if reason else []
    for rule in (watering_points, experience_points, weather_points):
        points, reason = rule(recommendation, plant)
        score += points
        if reason:
            reasons.append(reason)
    return score, reasons


def filter_plants(plants, sunlight="", difficulty=""):
    if sunlight in SUNLIGHT_FILTERS:
        plants = plants.filter(sunlight__icontains=SUNLIGHT_FILTERS[sunlight][1])
    if difficulty in DIFFICULTY_FILTERS:
        query = Q()
        for value in DIFFICULTY_FILTERS[difficulty][1]:
            query |= Q(difficulty__iexact=value)
        plants = plants.filter(query)
    return plants


def recommend_plants(recommendation, sunlight="", difficulty="", limit=DEFAULT_LIMIT):
    """Urutkan tanaman dari katalog berdasarkan kecocokan dengan preferensi user."""
    plants = filter_plants(Plant.objects.all(), sunlight, difficulty)
    matches = []
    for plant in plants:
        score, reasons = score_plant(recommendation, plant)
        if score > 0:
            matches.append({
                "plant": plant,
                "score": score,
                "match_percent": round(score / MAX_SCORE * 100),
                "reasons": reasons,
            })
    matches.sort(key=lambda match: (-match["score"], match["plant"].name.lower()))
    return matches[:limit]


def match_to_dict(match):
    plant = match["plant"]
    return {
        "id": str(plant.id),
        "name": plant.name,
        "scientific_name": plant.scientific_name,
        "image_url": plant.image_url,
        "indoor": plant.indoor,
        "sunlight": plant.sunlight,
        "watering": plant.watering,
        "difficulty": plant.difficulty,
        "match_percent": match["match_percent"],
        "reasons": match["reasons"],
    }
