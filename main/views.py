from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.formats import date_format
from django.views.decorators.http import require_POST

from .forms import PlantReviewForm
from .models import Plant, PlantReview


def show_main(request):
    return render(request, "index.html", {"brand": "growmatch"})


def is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def serialize_review(review):
    return {
        "id": review.pk,
        "username": review.user.username,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": date_format(review.created_at, "M j, Y"),
        "edit_url": reverse("main:edit_plant_review", args=[review.pk]),
        "delete_url": reverse("main:delete_plant_review", args=[review.pk]),
    }


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

            if is_ajax(request):
                return JsonResponse(
                    {"ok": True, "review": serialize_review(review)},
                    status=201,
                )
            return redirect("main:plant_review", plant_id=plant.pk)

        if is_ajax(request):
            return JsonResponse(
                {"ok": False, "errors": form.errors.get_json_data()},
                status=400,
            )
    else:
        form = PlantReviewForm()

    reviews = (
        PlantReview.objects.filter(plant=plant)
        .select_related("user")
        .order_by("-created_at", "-pk")
    )
    return render(
        request,
        "review_form.html",
        {"form": form, "plant": plant, "reviews": reviews},
    )


@login_required(login_url="/login/")
def edit_plant_review(request, review_id):
    review = get_object_or_404(PlantReview, pk=review_id, user=request.user)

    if request.method == "POST":
        form = PlantReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            if is_ajax(request):
                return JsonResponse(
                    {"ok": True, "review": serialize_review(review)}
                )
            return redirect("main:plant_review", plant_id=review.plant_id)

        if is_ajax(request):
            return JsonResponse(
                {"ok": False, "errors": form.errors.get_json_data()},
                status=400,
            )

        return render(
            request,
            "review_form.html",
            {
                "form": form,
                "plant": review.plant,
                "reviews": PlantReview.objects.filter(plant=review.plant).select_related("user"),
                "editing_review": review,
            },
        )

    return redirect("main:plant_review", plant_id=review.plant_id)


@login_required(login_url="/login/")
@require_POST
def delete_plant_review(request, review_id):
    review = get_object_or_404(PlantReview, pk=review_id, user=request.user)
    plant_id = review.plant_id
    review.delete()

    if is_ajax(request):
        return JsonResponse({"ok": True, "deleted_id": review_id})
    return redirect("main:plant_review", plant_id=plant_id)
