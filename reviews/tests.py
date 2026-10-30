from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import PlantReviewForm
from main.models import PlantReview
from plant_catalog.models import Plant


class PlantReviewFormTests(TestCase):
    def test_valid_form(self):
        form = PlantReviewForm(data={
            "rating": 5,
            "comment": "Very healthy and easy to care for."
        })

        self.assertTrue(form.is_valid())

    def test_invalid_form_when_rating_is_out_of_range(self):
        form = PlantReviewForm(data={
            "rating": 0,
            "comment": "This should fail."
        })

        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)


class PlantModelTests(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123"
        )

    def test_average_rating_returns_zero_when_no_reviews_exist(self):
        self.assertEqual(self.plant.average_rating, 0)

    def test_average_rating_is_calculated_across_reviews(self):
        PlantReview.objects.create(
            plant=self.plant,
            user=self.user,
            rating=4,
            comment="Strong growth"
        )
        PlantReview.objects.create(
            plant=self.plant,
            user=self.user,
            rating=2,
            comment="Needs more sunlight"
        )

        self.assertEqual(self.plant.average_rating, 3)


class PlantReviewModelTests(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create()
        self.user = get_user_model().objects.create_user(
            username="reviewer",
            password="testpassword123"
        )

    def test_rating_range_is_validated(self):
        review = PlantReview(
            plant=self.plant,
            user=self.user,
            rating=6,
            comment="Too high"
        )

        with self.assertRaises(ValidationError):
            review.full_clean()


class PlantReviewViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="plantlover",
            password="testpassword123"
        )
        self.plant = Plant.objects.create()
        self.client.force_login(self.user)

    def test_add_review_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("reviews:plant_review", args=[self.plant.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_add_review_get_displays_form_and_plant(self):
        response = self.client.get(
            reverse("reviews:plant_review", args=[self.plant.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["plant"], self.plant)
        self.assertIn("form", response.context)
        self.assertContains(response, "Submit Review")

    def test_add_review_post_creates_review_and_redirects(self):
        response = self.client.post(
            reverse("reviews:plant_review", args=[self.plant.pk]),
            {
                "rating": 5,
                "comment": "This plant is thriving!"
            }
        )

        self.assertRedirects(
            response,
            reverse("reviews:plant_review", args=[self.plant.pk])
        )
        self.assertTrue(
            PlantReview.objects.filter(
                plant=self.plant,
                user=self.user,
                rating=5,
                comment="This plant is thriving!"
            ).exists()
        )

    def test_edit_review_updates_only_the_user_owned_review(self):
        review = PlantReview.objects.create(
            plant=self.plant,
            user=self.user,
            rating=3,
            comment="Original comment"
        )

        response = self.client.post(
            reverse("reviews:edit_plant_review", args=[review.pk]),
            {
                "rating": 4,
                "comment": "Updated review"
            }
        )

        self.assertRedirects(
            response,
            reverse("reviews:plant_review", args=[self.plant.pk])
        )
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Updated review")

    def test_delete_review_removes_the_user_owned_review(self):
        review = PlantReview.objects.create(
            plant=self.plant,
            user=self.user,
            rating=2,
            comment="Temporary comment"
        )

        response = self.client.post(
            reverse("reviews:delete_plant_review", args=[review.pk])
        )

        self.assertRedirects(
            response,
            reverse("reviews:plant_review", args=[self.plant.pk])
        )
        self.assertFalse(PlantReview.objects.filter(pk=review.pk).exists())


class PlantReviewOwnershipTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="owner",
            password="testpassword123"
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            password="testpassword123"
        )
        self.plant = Plant.objects.create()
        self.review = PlantReview.objects.create(
            plant=self.plant,
            user=self.owner,
            rating=5,
            comment="Owner review"
        )

    def test_edit_review_returns_404_for_non_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("reviews:edit_plant_review", args=[self.review.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_review_returns_404_for_non_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("reviews:delete_plant_review", args=[self.review.pk])
        )

        self.assertEqual(response.status_code, 404)
