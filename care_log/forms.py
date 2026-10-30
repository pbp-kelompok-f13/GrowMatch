from django import forms

from my_garden.models import GardenPlant
from .models import CareActivity


class CareActivityForm(forms.ModelForm):
    class Meta:
        model = CareActivity
        fields = [
            "garden_plant",
            "activity_type",
            "activity_date",
            "notes",
        ]

        widgets = {
            "activity_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Apa yang kamu lakukan pada tanaman?",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")

        super().__init__(*args, **kwargs)

        self.fields["garden_plant"].queryset = (
            GardenPlant.objects.filter(
                user=user
            ).select_related("plant")
        )

        self.fields["garden_plant"].label_from_instance = (
            lambda item: item.nickname or item.plant.name
        )