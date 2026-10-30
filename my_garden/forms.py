from django import forms
from .models import GardenPlant


class GardenPlantForm(forms.ModelForm):
    class Meta:
        model = GardenPlant
        fields = ["nickname", "notes"]

        widgets = {
            "nickname": forms.TextInput(
                attrs={
                    "placeholder": "Contoh: Mawar di teras",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Catatan tentang tanaman ini...",
                }
            ),
        }