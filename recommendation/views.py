from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from recommendation.forms import RecommendationRequestForm
from recommendation.models import RecommendationRequest
from recommendation.scoring import DIFFICULTY_FILTERS, SUNLIGHT_FILTERS, match_to_dict, recommend_plants
from recommendation.weather import LocationNotFound, apply_location_and_weather

LOGIN_URL = "/login/"
WEATHER_UNAVAILABLE = "Data cuaca lagi nggak bisa diambil, rekomendasi tetap disimpan tanpa data cuaca."


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def get_own_recommendation(request, pk):
    return get_object_or_404(RecommendationRequest, pk=pk, user=request.user)


def save_recommendation_form(request, form):
    """Validasi form, ambil data Open-Meteo, lalu simpan.

    Mengembalikan objek yang tersimpan, atau None kalau form/lokasi tidak valid
    (error sudah ditambahkan ke form).
    """
    if not form.is_valid():
        return None

    recommendation = form.save(commit=False)
    recommendation.user = request.user
    try:
        weather_ok = apply_location_and_weather(recommendation)
    except LocationNotFound:
        form.add_error("location_name", "Lokasi tidak ditemukan. Coba tulis nama kota lain.")
        return None

    recommendation.save()
    if not weather_ok:
        messages.warning(request, WEATHER_UNAVAILABLE)
    return recommendation


def get_plant_filters(request):
    sunlight = request.GET.get("sunlight", "")
    difficulty = request.GET.get("difficulty", "")
    return {
        "sunlight": sunlight if sunlight in SUNLIGHT_FILTERS else "",
        "difficulty": difficulty if difficulty in DIFFICULTY_FILTERS else "",
    }


def form_response(request, form, recommendation, template, context):
    if recommendation is not None:
        detail_url = reverse("recommendation:detail", args=[recommendation.pk])
        if is_ajax(request):
            return JsonResponse({"ok": True, "redirect_url": detail_url, "data": recommendation.to_dict()})
        return redirect(detail_url)

    if is_ajax(request):
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    return render(request, template, {**context, "form": form}, status=400)


@require_GET
def show_recommendation_form(request):
    return render(request, "recommendation/form.html", {"form": RecommendationRequestForm()})


@login_required(login_url=LOGIN_URL)
@require_POST
def create_recommendation(request):
    form = RecommendationRequestForm(request.POST)
    recommendation = save_recommendation_form(request, form)
    return form_response(request, form, recommendation, "recommendation/form.html", {})


@login_required(login_url=LOGIN_URL)
@require_GET
def show_history(request):
    recommendations = RecommendationRequest.objects.filter(user=request.user)

    space_type = request.GET.get("space_type", "")
    if space_type in dict(RecommendationRequest.SPACE_CHOICES):
        recommendations = recommendations.filter(space_type=space_type)
    else:
        space_type = ""

    return render(request, "recommendation/history.html", {
        "recommendations": recommendations,
        "space_type": space_type,
        "space_choices": RecommendationRequest.SPACE_CHOICES,
    })


@login_required(login_url=LOGIN_URL)
@require_GET
def show_detail(request, pk):
    recommendation = get_own_recommendation(request, pk)
    filters = get_plant_filters(request)
    return render(request, "recommendation/detail.html", {
        "recommendation": recommendation,
        "matches": recommend_plants(recommendation, **filters),
        "filters": filters,
        "sunlight_choices": [(key, label) for key, (label, _) in SUNLIGHT_FILTERS.items()],
        "difficulty_choices": [(key, label) for key, (label, _) in DIFFICULTY_FILTERS.items()],
    })


@login_required(login_url=LOGIN_URL)
def edit_recommendation(request, pk):
    recommendation = get_own_recommendation(request, pk)

    if request.method == "POST":
        form = RecommendationRequestForm(request.POST, instance=recommendation)
        saved = save_recommendation_form(request, form)
        return form_response(request, form, saved, "recommendation/edit.html", {"recommendation": recommendation})

    form = RecommendationRequestForm(instance=recommendation)
    return render(request, "recommendation/edit.html", {"form": form, "recommendation": recommendation})


@login_required(login_url=LOGIN_URL)
@require_POST
def delete_recommendation(request, pk):
    recommendation = get_own_recommendation(request, pk)
    recommendation.delete()

    if is_ajax(request):
        return JsonResponse({"ok": True})
    messages.success(request, "Rekomendasi dihapus.")
    return redirect("recommendation:history")


@login_required(login_url=LOGIN_URL)
@require_GET
def show_json(request):
    recommendations = RecommendationRequest.objects.filter(user=request.user)
    return JsonResponse([recommendation.to_dict() for recommendation in recommendations], safe=False)


@login_required(login_url=LOGIN_URL)
@require_GET
def show_json_by_id(request, pk):
    recommendation = get_own_recommendation(request, pk)
    return JsonResponse(recommendation.to_dict())


@login_required(login_url=LOGIN_URL)
@require_GET
def show_plants_json(request, pk):
    recommendation = get_own_recommendation(request, pk)
    matches = recommend_plants(recommendation, **get_plant_filters(request))
    return JsonResponse([match_to_dict(match) for match in matches], safe=False)
