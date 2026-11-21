from rest_framework import serializers
from main.models import PlantReview

class PlantReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlantReview
        fields = [
            'id', 
            'plant', 
            'user', 
            'rating', 
            'comment', 
            'created_at', 
            'updated_at',
            ]
        read_only_fields = [
            'id', 
            'plant', 
            'user', 
            'created_at',
            'updated_at',
            ]
            
