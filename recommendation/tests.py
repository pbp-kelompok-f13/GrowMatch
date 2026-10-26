from unittest.mock import Mock, patch

import requests
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from recommendation import weather
from recommendation.forms import RecommendationRequestForm
from recommendation.models import RecommendationRequest

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
VALID_DATA = {
    "location_name": "Depok",
    "space_type": "indoor",
    "watering_frequency": "average",
    "experience_level": "beginner",
}
DEPOK = {"name": "Depok, Indonesia", "latitude": -6.4, "longitude": 106.8}
SUNNY = {"temperature": 30.5, "humidity": 75}


def mock_response(json_data):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


def make_recommendation(user, **kwargs):
    data = {
        "location_name": "Depok, Indonesia",
        "space_type": "indoor",
        "watering_frequency": "average",
        "experience_level": "beginner",
        "latitude": -6.4,
        "longitude": 106.8,
        "temperature": 30.5,
        "humidity": 75,
    }
    data.update(kwargs)
    return RecommendationRequest.objects.create(user=user, **data)


class RecommendationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("deo", password="pass12345")

    def test_str(self):
        recommendation = make_recommendation(self.user)
        self.assertEqual(str(recommendation), "deo - Depok, Indonesia (Indoor)")

    def test_has_weather(self):
        self.assertTrue(make_recommendation(self.user).has_weather)
        self.assertFalse(make_recommendation(self.user, temperature=None).has_weather)

    def test_to_dict(self):
        recommendation = make_recommendation(self.user)
        data = recommendation.to_dict()
        self.assertEqual(data["id"], str(recommendation.id))
        self.assertEqual(data["user"], "deo")
        self.assertEqual(data["temperature"], 30.5)

    def test_ordering_newest_first(self):
        old = make_recommendation(self.user, location_name="Old")
        new = make_recommendation(self.user, location_name="New")
        self.assertEqual(list(RecommendationRequest.objects.all()), [new, old])


class RecommendationFormTest(TestCase):
    def test_valid(self):
        self.assertTrue(RecommendationRequestForm(data=VALID_DATA).is_valid())

    def test_location_is_stripped(self):
        form = RecommendationRequestForm(data={**VALID_DATA, "location_name": "  Depok  "})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["location_name"], "Depok")

    def test_location_too_short(self):
        form = RecommendationRequestForm(data={**VALID_DATA, "location_name": " a "})
        self.assertIn("location_name", form.errors)

    def test_invalid_choice(self):
        form = RecommendationRequestForm(data={**VALID_DATA, "space_type": "balcony"})
        self.assertIn("space_type", form.errors)

    def test_missing_fields(self):
        form = RecommendationRequestForm(data={})
        self.assertEqual(
            set(form.errors),
            {"location_name", "space_type", "watering_frequency", "experience_level"},
        )


@patch("recommendation.weather.requests.get")
class WeatherServiceTest(TestCase):
    def test_geocode_success(self, mock_get):
        mock_get.return_value = mock_response(
            {"results": [{"name": "Depok", "country": "Indonesia", "latitude": -6.4, "longitude": 106.8}]}
        )
        self.assertEqual(weather.geocode("Depok"), DEPOK)

    def test_geocode_without_country(self, mock_get):
        mock_get.return_value = mock_response({"results": [{"name": "Depok", "latitude": 1, "longitude": 2}]})
        self.assertEqual(weather.geocode("Depok")["name"], "Depok")

    def test_geocode_not_found(self, mock_get):
        mock_get.return_value = mock_response({})
        with self.assertRaises(weather.LocationNotFound):
            weather.geocode("Antah Berantah")

    def test_geocode_api_down(self, mock_get):
        mock_get.side_effect = requests.ConnectionError
        self.assertIsNone(weather.geocode("Depok"))

    def test_weather_success(self, mock_get):
        mock_get.return_value = mock_response({"current": {"temperature_2m": 30.5, "relative_humidity_2m": 75}})
        self.assertEqual(weather.get_current_weather(-6.4, 106.8), SUNNY)

    def test_weather_bad_payload(self, mock_get):
        mock_get.return_value = mock_response({"error": True})
        self.assertIsNone(weather.get_current_weather(-6.4, 106.8))

    def test_weather_api_down(self, mock_get):
        mock_get.side_effect = requests.Timeout
        self.assertIsNone(weather.get_current_weather(-6.4, 106.8))


class ApplyLocationAndWeatherTest(TestCase):
    def setUp(self):
        self.recommendation = RecommendationRequest(location_name="Depok")

    @patch("recommendation.weather.get_current_weather", return_value=SUNNY)
    @patch("recommendation.weather.geocode", return_value=DEPOK)
    def test_success(self, mock_geocode, mock_weather):
        self.assertTrue(weather.apply_location_and_weather(self.recommendation))
        self.assertEqual(self.recommendation.location_name, "Depok, Indonesia")
        self.assertEqual(self.recommendation.temperature, 30.5)
        mock_weather.assert_called_once_with(-6.4, 106.8)

    @patch("recommendation.weather.geocode", return_value=None)
    def test_geocode_down(self, mock_geocode):
        self.recommendation.temperature = 20
        self.assertFalse(weather.apply_location_and_weather(self.recommendation))
        self.assertIsNone(self.recommendation.latitude)
        self.assertIsNone(self.recommendation.temperature)

    @patch("recommendation.weather.get_current_weather", return_value=None)
    @patch("recommendation.weather.geocode", return_value=DEPOK)
    def test_weather_down(self, mock_geocode, mock_weather):
        self.assertFalse(weather.apply_location_and_weather(self.recommendation))
        self.assertEqual(self.recommendation.latitude, -6.4)
        self.assertIsNone(self.recommendation.humidity)


class GuestAccessTest(TestCase):
    def test_form_page_is_public(self):
        response = self.client.get(reverse("recommendation:form"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recommendation/form.html")
        self.assertContains(response, "Login dulu")
        self.assertNotContains(response, 'type="submit"')

    def test_protected_pages_redirect_to_login(self):
        recommendation = make_recommendation(User.objects.create_user("other"))
        urls = [
            reverse("recommendation:history"),
            reverse("recommendation:detail", args=[recommendation.pk]),
            reverse("recommendation:edit", args=[recommendation.pk]),
            reverse("recommendation:json"),
            reverse("recommendation:json_by_id", args=[recommendation.pk]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertTrue(response.url.startswith("/login/"), url)

    def test_guest_cannot_create_or_delete(self):
        recommendation = make_recommendation(User.objects.create_user("other"))
        self.client.post(reverse("recommendation:create"), VALID_DATA)
        self.client.post(reverse("recommendation:delete", args=[recommendation.pk]))
        self.assertEqual(RecommendationRequest.objects.count(), 1)


@patch("recommendation.views.apply_location_and_weather")
class CreateRecommendationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("deo", password="pass12345")
        self.client.force_login(self.user)
        self.url = reverse("recommendation:create")

    def test_form_page_shows_submit_for_user(self, mock_apply):
        response = self.client.get(reverse("recommendation:form"))
        self.assertContains(response, "Get Your Match")
        self.assertContains(response, 'type="submit"')

    def test_create_redirects_to_detail(self, mock_apply):
        mock_apply.return_value = True
        response = self.client.post(self.url, VALID_DATA)
        recommendation = RecommendationRequest.objects.get()
        self.assertRedirects(response, reverse("recommendation:detail", args=[recommendation.pk]))
        self.assertEqual(recommendation.user, self.user)

    def test_create_ajax_returns_json(self, mock_apply):
        mock_apply.return_value = True
        response = self.client.post(self.url, VALID_DATA, **AJAX)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["data"]["location_name"], "Depok")
        self.assertIn(data["data"]["id"], data["redirect_url"])

    def test_create_when_weather_unavailable_still_saves(self, mock_apply):
        mock_apply.return_value = False
        response = self.client.post(self.url, VALID_DATA, follow=True)
        self.assertEqual(RecommendationRequest.objects.count(), 1)
        self.assertContains(response, "Data cuaca lagi nggak bisa diambil")

    def test_invalid_form(self, mock_apply):
        response = self.client.post(self.url, {**VALID_DATA, "space_type": ""})
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "recommendation/form.html")
        self.assertFalse(RecommendationRequest.objects.exists())
        mock_apply.assert_not_called()

    def test_invalid_form_ajax(self, mock_apply):
        response = self.client.post(self.url, {**VALID_DATA, "space_type": ""}, **AJAX)
        self.assertEqual(response.status_code, 400)
        self.assertIn("space_type", response.json()["errors"])

    def test_location_not_found(self, mock_apply):
        mock_apply.side_effect = weather.LocationNotFound
        response = self.client.post(self.url, VALID_DATA, **AJAX)
        self.assertEqual(response.status_code, 400)
        self.assertIn("location_name", response.json()["errors"])
        self.assertFalse(RecommendationRequest.objects.exists())

    def test_get_not_allowed(self, mock_apply):
        self.assertEqual(self.client.get(self.url).status_code, 405)


class OwnRecommendationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("deo", password="pass12345")
        self.other = User.objects.create_user("aisyah", password="pass12345")
        self.mine = make_recommendation(self.user, location_name="Depok, Indonesia")
        self.outdoor = make_recommendation(self.user, location_name="Bogor, Indonesia", space_type="outdoor")
        self.theirs = make_recommendation(self.other, location_name="Jakarta, Indonesia")
        self.client.force_login(self.user)

    def test_history_only_shows_own(self):
        response = self.client.get(reverse("recommendation:history"))
        self.assertContains(response, "Depok, Indonesia")
        self.assertContains(response, "Bogor, Indonesia")
        self.assertNotContains(response, "Jakarta, Indonesia")

    def test_history_filter_space_type(self):
        response = self.client.get(reverse("recommendation:history"), {"space_type": "outdoor"})
        self.assertEqual(list(response.context["recommendations"]), [self.outdoor])
        self.assertEqual(response.context["space_type"], "outdoor")

    def test_history_ignores_unknown_filter(self):
        response = self.client.get(reverse("recommendation:history"), {"space_type": "moon"})
        self.assertEqual(len(response.context["recommendations"]), 2)
        self.assertEqual(response.context["space_type"], "")

    def test_history_empty_filter_result(self):
        self.outdoor.delete()
        response = self.client.get(reverse("recommendation:history"), {"space_type": "outdoor"})
        self.assertContains(response, "Belum ada rekomendasi untuk filter ini")

    def test_detail(self):
        response = self.client.get(reverse("recommendation:detail", args=[self.mine.pk]))
        self.assertContains(response, "Depok, Indonesia")
        self.assertContains(response, "30.5°C")

    def test_detail_without_weather(self):
        recommendation = make_recommendation(self.user, temperature=None, humidity=None)
        response = self.client.get(reverse("recommendation:detail", args=[recommendation.pk]))
        self.assertContains(response, "Data cuaca belum tersedia")

    def test_cannot_access_others(self):
        for name in ["detail", "edit", "json_by_id"]:
            response = self.client.get(reverse(f"recommendation:{name}", args=[self.theirs.pk]))
            self.assertEqual(response.status_code, 404, name)
        response = self.client.post(reverse("recommendation:delete", args=[self.theirs.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(RecommendationRequest.objects.filter(pk=self.theirs.pk).exists())

    def test_edit_page(self):
        response = self.client.get(reverse("recommendation:edit", args=[self.mine.pk]))
        self.assertTemplateUsed(response, "recommendation/edit.html")
        self.assertContains(response, 'value="Depok, Indonesia"')

    @patch("recommendation.views.apply_location_and_weather", return_value=True)
    def test_edit_updates(self, mock_apply):
        url = reverse("recommendation:edit", args=[self.mine.pk])
        response = self.client.post(url, {**VALID_DATA, "space_type": "outdoor"})
        self.assertRedirects(response, reverse("recommendation:detail", args=[self.mine.pk]))
        self.mine.refresh_from_db()
        self.assertEqual(self.mine.space_type, "outdoor")
        self.assertEqual(RecommendationRequest.objects.filter(user=self.user).count(), 2)

    @patch("recommendation.views.apply_location_and_weather", return_value=True)
    def test_edit_invalid(self, mock_apply):
        url = reverse("recommendation:edit", args=[self.mine.pk])
        response = self.client.post(url, {**VALID_DATA, "experience_level": "god"})
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "recommendation/edit.html")
        self.mine.refresh_from_db()
        self.assertEqual(self.mine.experience_level, "beginner")

    def test_delete(self):
        response = self.client.post(reverse("recommendation:delete", args=[self.mine.pk]))
        self.assertRedirects(response, reverse("recommendation:history"))
        self.assertFalse(RecommendationRequest.objects.filter(pk=self.mine.pk).exists())

    def test_delete_ajax(self):
        response = self.client.post(reverse("recommendation:delete", args=[self.mine.pk]), **AJAX)
        self.assertEqual(response.json(), {"ok": True})
        self.assertFalse(RecommendationRequest.objects.filter(pk=self.mine.pk).exists())

    def test_delete_requires_post(self):
        response = self.client.get(reverse("recommendation:delete", args=[self.mine.pk]))
        self.assertEqual(response.status_code, 405)

    def test_json_list_only_own(self):
        data = self.client.get(reverse("recommendation:json")).json()
        self.assertEqual({item["id"] for item in data}, {str(self.mine.pk), str(self.outdoor.pk)})

    def test_json_by_id(self):
        data = self.client.get(reverse("recommendation:json_by_id", args=[self.mine.pk])).json()
        self.assertEqual(data["location_name"], "Depok, Indonesia")
