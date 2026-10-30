from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Plant


class PlantModelTest(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create(
            name="Monstera",
            scientific_name="Monstera deliciosa",
            sunlight="bright indirect",
            watering="Average",
            difficulty="Easy",
            indoor=True,
        )

    def test_plant_created(self):
        self.assertEqual(self.plant.name, "Monstera")
        self.assertEqual(
            self.plant.scientific_name,
            "Monstera deliciosa",
        )
        self.assertTrue(self.plant.indoor)

    def test_plant_string_representation(self):
        self.assertEqual(str(self.plant), "Monstera")


class PlantCatalogViewTest(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create(
            name="Monstera",
            sunlight="bright indirect",
            watering="Average",
            difficulty="Easy",
        )

    def test_catalog_page_loads(self):
        response = self.client.get(
            reverse("plant_catalog:catalog")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "plant_catalog/catalog.html",
        )

    def test_catalog_displays_plant(self):
        response = self.client.get(
            reverse("plant_catalog:catalog")
        )

        self.assertContains(response, "Monstera")

    def test_search_filters_plants_by_name(self):
        Plant.objects.create(
            name="Rose",
            sunlight="full sun",
            watering="Frequent",
            difficulty="Medium",
        )

        response = self.client.get(
            reverse("plant_catalog:catalog"),
            {"search": "Monstera"},
        )

        self.assertContains(response, "Monstera")
        self.assertNotContains(response, "Rose")

    def test_filter_by_watering(self):
        Plant.objects.create(
            name="Rose",
            sunlight="full sun",
            watering="Frequent",
            difficulty="Medium",
        )

        response = self.client.get(
            reverse("plant_catalog:catalog"),
            {"watering": "Average"},
        )

        self.assertContains(response, "Monstera")
        self.assertNotContains(response, "Rose")

    def test_filter_by_difficulty(self):
        Plant.objects.create(
            name="Rose",
            sunlight="full sun",
            watering="Frequent",
            difficulty="Medium",
        )

        response = self.client.get(
            reverse("plant_catalog:catalog"),
            {"difficulty": "Easy"},
        )

        self.assertContains(response, "Monstera")
        self.assertNotContains(response, "Rose")

    def test_ajax_catalog_returns_partial(self):
        response = self.client.get(
            reverse("plant_catalog:catalog_ajax"),
            {"search": "Monstera"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "plant_catalog/partials/plant_results.html",
        )
        self.assertContains(response, "Monstera")


class PlantCRUDTest(TestCase):
    def setUp(self):
        self.plant = Plant.objects.create(
            name="Monstera",
            sunlight="bright indirect",
            watering="Average",
            difficulty="Easy",
            indoor=True,
        )

        self.staff = User.objects.create_user(
            username="staff",
            password="testpass123",
            is_staff=True,
        )

        self.user = User.objects.create_user(
            username="user",
            password="testpass123",
        )

    def test_detail_page_loads(self):
        response = self.client.get(
            reverse(
                "plant_catalog:detail",
                args=[self.plant.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monstera")

    def test_staff_can_access_add_page(self):
        self.client.login(
            username="staff",
            password="testpass123",
        )

        response = self.client.get(
            reverse("plant_catalog:add")
        )

        self.assertEqual(response.status_code, 200)

    def test_normal_user_cannot_access_add_page(self):
        self.client.login(
            username="user",
            password="testpass123",
        )

        response = self.client.get(
            reverse("plant_catalog:add")
        )

        self.assertEqual(response.status_code, 302)

    def test_staff_can_access_edit_page(self):
        self.client.login(
            username="staff",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "plant_catalog:edit",
                args=[self.plant.id],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_normal_user_cannot_access_edit_page(self):
        self.client.login(
            username="user",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "plant_catalog:edit",
                args=[self.plant.id],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_staff_can_delete_plant(self):
        self.client.login(
            username="staff",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "plant_catalog:delete",
                args=[self.plant.id],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Plant.objects.filter(id=self.plant.id).exists()
        )

    def test_normal_user_cannot_delete_plant(self):
        self.client.login(
            username="user",
            password="testpass123",
        )

        self.client.post(
            reverse(
                "plant_catalog:delete",
                args=[self.plant.id],
            )
        )

        self.assertTrue(
            Plant.objects.filter(id=self.plant.id).exists()
        )

    def test_staff_can_add_plant(self):
        self.client.login(
            username="staff",
            password="testpass123",
        )

        response = self.client.post(
            reverse("plant_catalog:add"),
            {
                "name": "Snake Plant",
                "scientific_name": "Dracaena trifasciata",
                "sunlight": "bright indirect",
                "watering": "Minimum",
                "difficulty": "Easy",
                "indoor": "True",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Plant.objects.filter(name="Snake Plant").exists()
        )

    def test_staff_can_edit_plant(self):
        self.client.login(
            username="staff",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "plant_catalog:edit",
                args=[self.plant.id],
            ),
            {
                "name": "Updated Monstera",
                "sunlight": "full sun",
                "watering": "Frequent",
                "difficulty": "Medium",
                "indoor": "True",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.plant.refresh_from_db()

        self.assertEqual(
            self.plant.name,
            "Updated Monstera",
        )
        self.assertEqual(
            self.plant.watering,
            "Frequent",
        )