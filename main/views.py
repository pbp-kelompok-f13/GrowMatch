from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Plant, PlantReview
from .forms import PlantReviewForm

def show_main(request):
    return render(request, "index.html", {"brand":"growmatch"})

@login_required(login_url="/login/")
def add_plant_review(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)

    if request.method == "POST":
        form = PlantReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.plant = plant
            review.user = request.user
            review.save()

            return redirect("plant_review", plant_id=plant.pk)

    else:
        form = PlantReviewForm()

    return render(request, "plants/review_form.html", {
        "form": form,
        "plant": plant
    })


@login_required(login_url="/login/")
def edit_plant_review(request, review_id):
    review = get_object_or_404(
        PlantReview,
        pk=review_id,
        user=request.user
    )

    if request.method == "POST":
        form = PlantReviewForm(request.POST, instance=review)

        if form.is_valid():
            form.save()

            return redirect(
                "plant_review",
                plant_id=review.plant_id
            )

    else:
        form = PlantReviewForm(instance=review)

    return render(request, "plants/edit_review.html", {
        "form": form,
        "review": review
    })


@login_required(login_url="/login/")
@require_POST
def delete_plant_review(request, review_id):
    review = get_object_or_404(
        PlantReview,
        pk=review_id,
        user=request.user
    )

    plant_id = review.plant_id
    review.delete()

    return redirect("plant_review", plant_id=plant_id)

