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

    # Judul, deskripsi, dan ikon untuk tiap pilihan di tampilan kartu
    OPTION_DETAILS = {
        "space_type": {
            "indoor": ("Indoor", "Di dalam rumah, kamar, atau kantor", "home"),
            "outdoor": ("Outdoor", "Teras, balkon, atau halaman", "sun"),
        },
        "watering_frequency": {
            "frequent": ("Sering", "Hampir setiap hari", "drop-3"),
            "average": ("Sedang", "2-3 kali seminggu", "drop-2"),
            "minimum": ("Jarang", "Seminggu sekali atau kurang", "drop-1"),
        },
    }
    STEP_HELP = {
        "location_name": "Kami pakai lokasi ini buat ambil suhu dan kelembapan dari Open-Meteo.",
        "space_type": "Pilih tempat tanamanmu bakal tumbuh.",
        "watering_frequency": "Jujur aja, nggak ada jawaban yang salah.",
        "experience_level": "Biar tanaman yang muncul sesuai kemampuanmu.",
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
            raise forms.ValidationError("Nama lokasi minimal 2 karakter.")
        return location_name
