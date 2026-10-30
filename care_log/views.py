from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CareActivityForm
from .models import CareActivity


@login_required
def care_log_view(request):
    activities = CareActivity.objects.filter(
        user=request.user
    ).select_related(
        "garden_plant",
        "garden_plant__plant",
    )

    return render(
        request,
        "care_log/index.html",
        {
            "activities": activities,
        },
    )


@login_required
def add_activity(request):
    if request.method == "POST":
        form = CareActivityForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()

            messages.success(
                request,
                "Catatan perawatan berhasil ditambahkan.",
            )

            return redirect("care_log:index")
    else:
        form = CareActivityForm(user=request.user)

    return render(
        request,
        "care_log/form.html",
        {"form": form},
    )


@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(
        CareActivity,
        pk=activity_id,
        user=request.user,
    )

    if request.method == "POST":
        form = CareActivityForm(
            request.POST,
            instance=activity,
            user=request.user,
        )

        if form.is_valid():
            updated_activity = form.save(commit=False)
            updated_activity.user = request.user
            updated_activity.save()

            messages.success(
                request,
                "Catatan perawatan berhasil diperbarui.",
            )

            return redirect("care_log:index")
    else:
        form = CareActivityForm(
            instance=activity,
            user=request.user,
        )

    return render(
        request,
        "care_log/form.html",
        {
            "form": form,
            "activity": activity,
        },
    )


@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(
        CareActivity,
        pk=activity_id,
        user=request.user,
    )

    if request.method == "POST":
        activity.delete()

        messages.success(
            request,
            "Catatan perawatan berhasil dihapus.",
        )

    return redirect("care_log:index")