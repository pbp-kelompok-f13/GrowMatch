from django import forms

from recommendation.models import RecommendationRequest


class RecommendationRequestForm(forms.ModelForm):
    class Meta:
        model = RecommendationRequest
        fields = ["location_name", "space_type", "watering_frequency", "experience_level"]
        labels = {
            "location_name": "Your city",
            "space_type": "Where will your plants live?",
            "watering_frequency": "How often can you water them?",
            "experience_level": "Plant care experience",
        }
        widgets = {
            "location_name": forms.TextInput(attrs={"placeholder": "e.g. Depok"}),
            "space_type": forms.RadioSelect,
            "watering_frequency": forms.RadioSelect,
            "experience_level": forms.RadioSelect,
        }

    # Judul, deskripsi, dan ikon untuk tiap pilihan di tampilan kartu
    OPTION_DETAILS = {
        "space_type": {
            "indoor": ("Indoor", "Inside your home, bedroom, or office", "home"),
            "outdoor": ("Outdoor", "Porch, balcony, or garden", "sun"),
        },
        "watering_frequency": {
            "frequent": ("Often", "Almost every day", "drop-3"),
            "average": ("Sometimes", "2-3 times a week", "drop-2"),
            "minimum": ("Rarely", "Once a week or less", "drop-1"),
        },
    }
    STEP_HELP = {
        "location_name": "We use this to get temperature and humidity from Open-Meteo.",
        "space_type": "Pick where your plants will grow.",
        "watering_frequency": "Be honest, there is no wrong answer.",
        "experience_level": "So we only suggest plants you can handle.",
    }

    def steps(self):
        """Data per langkah untuk template form bernomor 01-04."""
        steps = []
        for number, name in enumerate(self.Meta.fields, start=1):
            field = self[name]
            step = {"number": f"{number:02d}", "field": field, "help": self.STEP_HELP[name], "options": []}
            if name != "location_name":
                selected = str(field.value() or "")
                details = self.OPTION_DETAILS.get(name, {})
                choices = [(value, label) for value, label in field.field.choices if value]
                for index, (value, label) in enumerate(choices):
                    title, description, icon = details.get(value, (label, "", ""))
                    step["options"].append({
                        "id": f"id_{name}_{index}",
                        "value": value,
                        "title": title,
                        "description": description,
                        "icon": icon,
                        "checked": value == selected,
                    })
                step["style"] = "cards" if details else "pills"
            steps.append(step)
        return steps

    def clean_location_name(self):
        location_name = self.cleaned_data["location_name"].strip()
        if len(location_name) < 2:
            raise forms.ValidationError("Location must be at least 2 characters.")
        return location_name
