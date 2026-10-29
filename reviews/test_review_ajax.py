from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from main.models import Plant, PlantReview


class PlantReviewAjaxTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", password="testpassword123"
        )
        self.plant = Plant.objects.create()
        self.client.force_login(self.user)
        self.create_url = reverse("reviews:plant_review", args=[self.plant.pk])
        self.ajax = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    def test_create_review_ajax(self):
        response = self.client.post(
            self.create_url, {"rating": 5, "comment": "Great!"}, **self.ajax
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["review"]["rating"], 5)
        self.assertEqual(PlantReview.objects.count(), 1)

    def test_invalid_review_returns_validation_errors(self):
        response = self.client.post(
            self.create_url, {"rating": 6, "comment": "Not valid"}, **self.ajax
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("rating", response.json()["errors"])
        self.assertEqual(PlantReview.objects.count(), 0)

    def test_edit_review_ajax(self):
        review = PlantReview.objects.create(
            plant=self.plant, user=self.user, rating=3, comment="Before"
        )
        response = self.client.post(
            reverse("reviews:edit_plant_review", args=[review.pk]),
            {"rating": 4, "comment": "After"},
            **self.ajax,
        )
        self.assertEqual(response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "After")

    def test_delete_review_ajax(self):
        review = PlantReview.objects.create(
            plant=self.plant, user=self.user, rating=3
        )
        response = self.client.post(
            reverse("reviews:delete_plant_review", args=[review.pk]), **self.ajax
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(PlantReview.objects.filter(pk=review.pk).exists())
