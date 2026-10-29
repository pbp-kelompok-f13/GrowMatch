from django import forms
from .models import Plant


class PlantForm(forms.ModelForm):
    indoor = forms.TypedChoiceField(
        choices=[
            (True, "Indoor"),
            (False, "Outdoor"),
        ],
        coerce=lambda value: value == "True",
        label="Placement",
    )
    soil = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "e.g. Well-draining, peat-based potting mix"}))
    propagation = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "e.g. Stem cuttings with a node"}))
    pruning_month = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "e.g. March, April, May"}))

    class Meta:
        model = Plant
        fields = [
            "name",
            "scientific_name",
            "description",
            "image_url",
            "indoor",
            "sunlight",
            "watering",
            "difficulty",
            "soil",
            "propagation",
            "pruning_month",
            "growth_rate",
            "maintenance",
            "watering_interval",
        ]

        labels = {
            "name": "Common name",
            "scientific_name": "Scientific name",
            "description": "Short description",
            "image_url": "Plant image URL",
            "indoor": "Placement",
            "sunlight": "Light",
            "watering": "Watering",
            "difficulty": "Difficulty",
            "soil": "Soil",
            "propagation": "Propagation",
            "pruning_month": "Pruning months",
            "growth_rate": "Growth rate",
            "maintenance": "Maintenance",
            "watering_interval": "Watering interval",
        }

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Monstera"}),
            "scientific_name": forms.TextInput(attrs={"placeholder": "e.g. Monstera deliciosa"}),
            "description": forms.Textarea(attrs={"placeholder": "A short, natural introduction...", "rows": 3}),
            "image_url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "sunlight": forms.TextInput(attrs={"placeholder": "e.g. Bright, indirect"}),
            "watering": forms.TextInput(attrs={"placeholder": "e.g. Moderate"}),
            "difficulty": forms.TextInput(attrs={"placeholder": "e.g. Easy"}),
            "soil": forms.TextInput(attrs={"placeholder": "e.g. Well-draining, peat-based potting mix"}),
            "propagation": forms.TextInput(attrs={"placeholder": "e.g. Stem cuttings with a node"}),
            "pruning_month": forms.TextInput(attrs={"placeholder": "e.g. March, April, May"}),
            "growth_rate": forms.TextInput(attrs={"placeholder": "e.g. Moderate to fast"}),
            "maintenance": forms.TextInput(attrs={"placeholder": "e.g. Low"}),
            "watering_interval": forms.TextInput(attrs={"placeholder": "e.g. 7-10 days"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.initial["soil"] = ", ".join(self.instance.soil or [])
            self.initial["propagation"] = ", ".join(self.instance.propagation or [])
            self.initial["pruning_month"] = ", ".join(self.instance.pruning_month or [])

    def clean_soil(self):
        value = self.cleaned_data.get("soil")
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def clean_propagation(self):
        value = self.cleaned_data.get("propagation")
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def clean_pruning_month(self):
        value = self.cleaned_data.get("pruning_month")
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value