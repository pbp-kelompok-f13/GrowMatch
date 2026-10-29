from django.shortcuts import get_object_or_404, render
from .models import Plant


def plant_catalog(request):
    plants = Plant.objects.all().order_by("name")

    search = request.GET.get("search", "").strip()
    sunlight = request.GET.get("sunlight", "").strip()
    watering = request.GET.get("watering", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()

    if search:
        plants = plants.filter(name__icontains=search)

    if sunlight:
        plants = plants.filter(sunlight__iexact=sunlight)

    if watering:
        plants = plants.filter(watering__iexact=watering)

    if difficulty:
        plants = plants.filter(difficulty__iexact=difficulty)

    sunlight_options = (
        Plant.objects.exclude(sunlight="")
        .values_list("sunlight", flat=True)
        .distinct()
        .order_by("sunlight")
    )

    watering_options = (
        Plant.objects.exclude(watering="")
        .values_list("watering", flat=True)
        .distinct()
        .order_by("watering")
    )

    difficulty_options = (
        Plant.objects.exclude(difficulty="")
        .values_list("difficulty", flat=True)
        .distinct()
        .order_by("difficulty")
    )

    context = {
        "plants": plants,
        "search": search,
        "sunlight": sunlight,
        "watering": watering,
        "difficulty": difficulty,
        "sunlight_options": sunlight_options,
        "watering_options": watering_options,
        "difficulty_options": difficulty_options,
    }

    return render(request, "plant_catalog/catalog.html", context)


def plant_detail(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)

    return render(
        request,
        "plant_catalog/detail.html",
        {"plant": plant},
    )