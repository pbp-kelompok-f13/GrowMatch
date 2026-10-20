from django import forms
from .models import PlantReview

class PlantReviewForm(forms.ModelForm):
    class Meta:
        model = PlantReview
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.NumberInput(attrs={
                "min": 1,
                "max": 5
            }),
            "comment": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Write your review..."
            })
        }