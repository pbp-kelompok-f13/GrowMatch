from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from .models import Plant
from .forms import PlantForm
from main.models import PlantReview

def staff_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff
    )(view_func)

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

def plant_catalog_ajax(request):
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

    context = {
        "plants": plants,
    }

    return render(
        request,
        "plant_catalog/partials/plant_results.html",
        context,
    )

def plant_detail(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)

    reviews = (PlantReview.objects.filter(plant=plant).select_related("user").order_by("-created_at", "-pk"))
    context = {"plant": plant, "reviews": reviews}

    return render(request, "plant_catalog/detail.html", context)

@staff_required
def add_plant(request):
    form = PlantForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        plant = form.save()
        messages.success(request, f"{plant.name} was added to the catalog.")
        return redirect("plant_catalog:detail", plant_id=plant.id)

    context = {
        "form": form,
        "page_title": "Add a new plant",
        "submit_label": "Add plant",
    }

    return render(request, "plant_catalog/plant_form.html", context)

@staff_required
def edit_plant(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)
    form = PlantForm(request.POST or None, instance=plant)

    if request.method == "POST" and form.is_valid():
        plant = form.save()
        messages.success(request, f"{plant.name} was updated successfully.")
        return redirect("plant_catalog:detail", plant_id=plant.id)

    context = {
        "form": form,
        "plant": plant,
        "page_title": "Edit plant",
        "submit_label": "Save changes",
    }

    return render(request, "plant_catalog/plant_form.html", context)

@staff_required
def delete_plant(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)

    if request.method == "POST":
        plant_name = plant.name
        plant.delete()
        messages.success(request, f"{plant_name} was removed from the catalog.")
        return redirect("plant_catalog:catalog")

    return render(request, "plant_catalog/plant_delete.html", {"plant": plant})