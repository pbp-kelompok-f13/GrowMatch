from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import *

from django.shortcuts import get_object_or_404

from .serializers import PlantReviewSerializer
from main.models import PlantReview
from plant_catalog.models import Plant


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def api_add_review(request: Request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)

    if request.method == "GET":
        plant_reviews = PlantReview.objects.filter(plant=plant)
        serializer = PlantReviewSerializer(plant_reviews, many=True)
        return Response(serializer.data)
    
    if request.method == "POST":
        serializer = PlantReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, plant=plant)
            return Response(
                status=status.HTTP_201_CREATED, 
                data=serializer.data
                )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_edit_or_delete_review(request: Request, review_id):

    review = get_object_or_404(PlantReview, pk=review_id)

    if review.user != request.user:
        return Response(
            status=status.HTTP_403_FORBIDDEN,
            data="You cannot edit or delete another user's review"
        )
    
    if request.method == 'DELETE':
        review.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    
    if request.method == 'PATCH':
        serializer = PlantReviewSerializer(
            review, 
            data=request.data, 
            partial=True
            )
        if serializer.is_valid():
            serializer.save()
            return Response(
                status=status.HTTP_200_OK,
                data=serializer.data
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )