from django.utils import timezone

from recommendation.models import PerenualLookup
from recommendation.perenual import PerenualError, fetch_new_plants, get_api_key
from recommendation.scoring import recommend_plants

MIN_RESULTS = 3
USER_DAILY_LIMIT = 2
GLOBAL_DAILY_LIMIT = 20
NEW_PLANTS_PER_LOOKUP = 2

MESSAGES = {
    "user_limit": "You've used today's 2 extra searches. Try again tomorrow.",
    "global_limit": "Extra searches are paused for today. Try again tomorrow.",
    "error": "Couldn't reach the plant database right now. Showing saved plants only.",
    "none_found": "No new plants found on Perenual for these answers.",
}


def lookups_today():
    return PerenualLookup.objects.filter(created_at__date=timezone.localdate())


def lookups_left(user):
    used = lookups_today().filter(user=user).count()
    return max(0, USER_DAILY_LIMIT - used)


def recommend_with_fallback(user, recommendation, sunlight="", difficulty=""):
    """Rekomendasi dari database, ditambah tanaman dari Perenual kalau hasilnya kurang.

    Mengembalikan (matches, status). status berisi enabled, lookups_left,
    added, dan message buat ditampilin ke user.
    """
    matches = recommend_plants(recommendation, sunlight, difficulty)
    api_key = get_api_key()
    status = {
        "enabled": bool(api_key),
        "lookups_left": lookups_left(user),
        "added": 0,
        "message": "",
    }
    if not api_key or len(matches) >= MIN_RESULTS:
        return matches, status

    if status["lookups_left"] == 0:
        status["message"] = MESSAGES["user_limit"]
        return matches, status
    if lookups_today().count() >= GLOBAL_DAILY_LIMIT:
        status["message"] = MESSAGES["global_limit"]
        return matches, status

    lookup = PerenualLookup.objects.create(user=user, recommendation=recommendation)
    status["lookups_left"] -= 1
    try:
        plants = fetch_new_plants(api_key, recommendation, sunlight, NEW_PLANTS_PER_LOOKUP)
    except PerenualError:
        status["message"] = MESSAGES["error"]
        return matches, status

    lookup.success = True
    lookup.plants_added = len(plants)
    lookup.save(update_fields=["success", "plants_added"])

    if not plants:
        status["message"] = MESSAGES["none_found"]
        return matches, status

    status["added"] = len(plants)
    noun = "plant" if len(plants) == 1 else "plants"
    status["message"] = f"We found {len(plants)} more {noun} from Perenual for you."
    return recommend_plants(recommendation, sunlight, difficulty), status
