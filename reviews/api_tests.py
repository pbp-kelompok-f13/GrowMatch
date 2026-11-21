from rest_framework.test import APITestCase
from django.urls import reverse
from plant_catalog.models import Plant
from main.models import PlantReview
from django.contrib.auth import get_user_model
import uuid

class PlantReviewAPITests(APITestCase):
    def setUp(self):
        self.plant = Plant.objects.create(
            name="Test Plant"
        )
        User = get_user_model()

        self.user = User.objects.create_user(
            username="test_user",
            password="test_pass",
        )

    def test_get_empty(self):
        url = reverse(
            "reviews:api_add_review", 
            kwargs={"plant_id":self.plant.pk}
            )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_invalid_plant(self):
        invalid_plant_id = uuid.uuid4()
        url = reverse(
            "reviews:api_add_review", 
            kwargs={"plant_id": invalid_plant_id}
            )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_review(self):

        review = PlantReview.objects.create(
            plant=self.plant,
            rating=5,
            user=self.user,
            comment='test comment'
        )
        
        url = reverse(
            "reviews:api_add_review", 
            kwargs={"plant_id":self.plant.pk}
            )
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], review.id)
        self.assertEqual(response.data[0]["rating"], review.rating)
        self.assertEqual(response.data[0]["comment"], review.comment)
        self.assertEqual(len(response.data), 1)

    def test_post_review(self):

        self.client.force_authenticate(user=self.user)

        data = {
            "rating": 5,
            "comment": 'test comment'
        }

        url = reverse(
            "reviews:api_add_review", 
            kwargs={"plant_id":self.plant.pk}
            )
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["rating"], data["rating"])
        self.assertEqual(response.data["comment"], data["comment"])
        self.assertEqual(PlantReview.objects.count(), 1)

    def test_unauthenticated_post_review(self):
        
        data = {
            "rating": 5,
            "comment": 'test comment'
        }

        url = reverse(
            "reviews:api_add_review", 
            kwargs={"plant_id":self.plant.pk}
            )
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_invalid_data_post_review(self):

        self.client.force_authenticate(user=self.user)

        data = {
            "rating": 6,
            "comment": 'test comment'
        }

        url = reverse(
            "reviews:api_add_review", 
            kwargs={"plant_id":self.plant.pk}
            )
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_patch_review(self):
    
        self.client.force_authenticate(user=self.user)

        review = PlantReview.objects.create(
            plant=self.plant,
            rating=1,
            user=self.user,
            comment='old comment'
        )

        new_data = {
            "rating": 5,
            "comment": 'new comment'
        }

        url = reverse(
            "reviews:api_edit_or_delete_review", 
            kwargs={"review_id":review.pk}
            )
        
        response = self.client.patch(url, new_data)

        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data["rating"], new_data["rating"])
        self.assertEqual(response.data["comment"], new_data["comment"])
        review.refresh_from_db()

        self.assertEqual(review.rating, new_data["rating"])
        self.assertEqual(review.comment, new_data["comment"])

    def test_delete_review(self):
        
        self.client.force_authenticate(user=self.user)

        review = PlantReview.objects.create(
            plant=self.plant,
            rating=1,
            user=self.user,
            comment='old comment'
        )

        url = reverse(
            "reviews:api_edit_or_delete_review", 
            kwargs={"review_id":review.pk}
            )
        
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            PlantReview.objects.filter(pk=review.pk).exists()
        )
