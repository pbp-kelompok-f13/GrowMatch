from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from plant_catalog.models import Plant
from .forms import GardenPlantForm
from .models import GardenPlant


@login_required
def my_garden_view(request):
    garden_plants = GardenPlant.objects.filter(
        user=request.user
    ).select_related("plant")

    return render(
        request,
        "my_garden/index.html",
        {"garden_plants": garden_plants},
    )


@login_required
def add_to_garden(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)

    if request.method != "POST":
        return redirect("plant_catalog:detail", plant_id=plant.pk)

    garden_plant, created = GardenPlant.objects.get_or_create(
        user=request.user,
        plant=plant,
    )

    if created:
        messages.success(
            request,
            f"{plant.name} berhasil ditambahkan ke My Garden.",
        )
    else:
        messages.info(
            request,
            f"{plant.name} sudah ada di My Garden.",
        )

    return redirect("my_garden:index")


@login_required
def edit_garden_plant(request, garden_plant_id):
    garden_plant = get_object_or_404(
        GardenPlant,
        pk=garden_plant_id,
        user=request.user,
    )

    if request.method == "POST":
        form = GardenPlantForm(
            request.POST,
            instance=garden_plant,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Informasi tanaman berhasil diperbarui.",
            )
            return redirect("my_garden:index")
    else:
        form = GardenPlantForm(instance=garden_plant)

    return render(
        request,
        "my_garden/edit.html",
        {
            "form": form,
            "garden_plant": garden_plant,
        },
    )


@login_required
def remove_from_garden(request, garden_plant_id):
    garden_plant = get_object_or_404(
        GardenPlant,
        pk=garden_plant_id,
        user=request.user,
    )

    if request.method == "POST":
        plant_name = garden_plant.plant.name
        garden_plant.delete()

        messages.success(
            request,
            f"{plant_name} berhasil dihapus dari My Garden.",
        )

    return redirect("my_garden:index")