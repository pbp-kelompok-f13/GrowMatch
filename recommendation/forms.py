from django import forms

from recommendation.models import RecommendationRequest


class RecommendationRequestForm(forms.ModelForm):
    class Meta:
        model = RecommendationRequest
        fields = ["location_name", "space_type", "watering_frequency", "experience_level"]
        labels = {
            "location_name": "Kota tempat tinggal",
            "space_type": "Tanamannya mau ditaruh di mana?",
            "watering_frequency": "Seberapa sering kamu bisa menyiram?",
            "experience_level": "Pengalaman merawat tanaman",
        }
        widgets = {
            "location_name": forms.TextInput(attrs={"placeholder": "Contoh: Depok"}),
            "space_type": forms.RadioSelect,
            "watering_frequency": forms.RadioSelect,
            "experience_level": forms.RadioSelect,
        }

    def clean_location_name(self):
        location_name = self.cleaned_data["location_name"].strip()
        if len(location_name) < 2:
            raise forms.ValidationError("Nama lokasi minimal 2 karakter.")
        return location_name
