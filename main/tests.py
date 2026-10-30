from django.test import TestCase
from django.urls import reverse


class HomepageTest(TestCase):
    def test_buttons_link_to_recommendation_and_catalog(self):
        response = self.client.get(reverse("main:homepage"))
        self.assertEqual(response.status_code, 200)
        match_url = reverse("recommendation:form")
        catalog_url = reverse("plant_catalog:catalog")
        self.assertContains(response, f'<a href="{match_url}" class="button--accent">')
        self.assertContains(response, f'<a href="{match_url}" class="button">', count=2)
        self.assertContains(response, f'<a href="{catalog_url}" class="button--secondary">', count=2)
