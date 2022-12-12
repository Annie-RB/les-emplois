import json

from django.urls import reverse

from itou.cities.factories import create_test_cities
from itou.jobs.factories import create_test_romes_and_appellations
from itou.jobs.models import Appellation
from itou.siaes.factories import SiaeFactory
from itou.utils.test import TestCase


class JobsAutocompleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase.
        create_test_romes_and_appellations(["N1101", "N4105"])
        # Update:
        # - autocomplete URL now needs a SIAE parameter (for existing ROME filtering)
        # - this URL does not accept create / update / delete of elements (removed some some tests)
        cls.siae = SiaeFactory()
        cls.url = reverse("autocomplete:jobs")

    def test_search_multi_words(self):
        response = self.client.get(
            self.url,
            {
                "term": "cariste ferroviaire",
                "siae_id": self.siae.id,
            },
        )
        assert response.status_code == 200
        expected = [
            {
                "value": "Agent / Agente cariste de livraison ferroviaire (N1101)",
                "code": "10357",
                "rome": "N1101",
                "name": "Agent / Agente cariste de livraison ferroviaire",
            }
        ]
        assert json.loads(response.content) == expected

    def test_search_case_insensitive_and_explicit_rome_code(self):
        response = self.client.get(
            self.url,
            {
                "term": "CHAUFFEUR livreuse n4105",
                "siae_id": self.siae.id,
            },
        )
        assert response.status_code == 200
        expected = [
            {
                "value": "Chauffeur-livreur / Chauffeuse-livreuse (N4105)",
                "code": "11999",
                "rome": "N4105",
                "name": "Chauffeur-livreur / Chauffeuse-livreuse",
            }
        ]
        assert json.loads(response.content) == expected

    def test_search_empty_chars(self):
        response = self.client.get(
            self.url,
            {
                "term": "    ",
                "siae_id": self.siae.id,
            },
        )
        assert response.status_code == 200
        expected = b"[]"
        assert response.content == expected

    def test_search_full_label(self):
        response = self.client.get(
            self.url,
            {
                "term": "Conducteur / Conductrice de chariot élévateur de l'armée (N1101)",
                "siae_id": self.siae.id,
            },
        )
        assert response.status_code == 200
        expected = [
            {
                "value": "Conducteur / Conductrice de chariot élévateur de l'armée (N1101)",
                "code": "12918",
                "rome": "N1101",
                "name": "Conducteur / Conductrice de chariot élévateur de l'armée",
            }
        ]
        assert json.loads(response.content) == expected

    def test_search_special_chars(self):
        response = self.client.get(
            self.url,
            {
                "term": "conducteur:* & & de:* & !chariot:* & <eleva:*>>>> & armee:* & `(((()))`):*",
                "siae_id": self.siae.id,
            },
        )
        assert response.status_code == 200
        expected = [
            {
                "value": "Conducteur / Conductrice de chariot élévateur de l'armée (N1101)",
                "code": "12918",
                "rome": "N1101",
                "name": "Conducteur / Conductrice de chariot élévateur de l'armée",
            }
        ]
        assert json.loads(response.content) == expected

    def test_search_filter_with_rome_code(self):
        appellation = Appellation.objects.autocomplete("conducteur", limit=1, rome_code="N1101")[0]
        assert appellation.code == "12918"
        assert appellation.name == "Conducteur / Conductrice de chariot élévateur de l'armée"

        appellation = Appellation.objects.autocomplete("conducteur", limit=1, rome_code="N4105")[0]
        assert appellation.code == "12859"
        assert appellation.name == "Conducteur collecteur / Conductrice collectrice de lait"


class CitiesAutocompleteTest(TestCase):
    def test_autocomplete(self):

        create_test_cities(["67"], num_per_department=10)

        url = reverse("autocomplete:cities")

        response = self.client.get(url, {"term": "alte"})
        assert response.status_code == 200
        expected = [
            {"value": "Altenheim (67)", "slug": "altenheim-67"},
            {"value": "Altorf (67)", "slug": "altorf-67"},
            {"value": "Alteckendorf (67)", "slug": "alteckendorf-67"},
            {"value": "Albé (67)", "slug": "albe-67"},
            {"value": "Altwiller (67)", "slug": "altwiller-67"},
        ]
        assert json.loads(response.content) == expected

        response = self.client.get(url, {"term": "    "})
        assert response.status_code == 200
        expected = b"[]"
        assert response.content == expected

        response = self.client.get(url, {"term": "paris"})
        assert response.status_code == 200
        expected = b"[]"
        assert response.content == expected
