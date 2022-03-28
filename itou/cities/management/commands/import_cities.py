import json
import os

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from itou.cities.models import City
from itou.common_apps.address.departments import DEPARTMENTS, department_from_postcode
from itou.utils.management_commands import DeprecatedLoggerMixin


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

# Use the data generated by `django-admin generate_cities`.
CITIES_JSON_FILE = f"{CURRENT_DIR}/data/cities.json"

MISSING_COORDS = {
    ("Miquelon-Langlade", "97501"): {"type": "Point", "coordinates": [-56.379167, 47.1]},
    ("Saint-Pierre", "97502"): {"type": "Point", "coordinates": [55.4778, -21.3419]},
    ("Saint-Barthélemy", "97701"): {"type": "Point", "coordinates": [-62.8342438, 17.897728]},
    ("Saint-Martin", "97801"): {"type": "Point", "coordinates": [-63.0668, 18.0603]},
}


class Command(DeprecatedLoggerMixin, BaseCommand):
    """
    Import French cities data from a JSON file into the database.

    To debug:
        django-admin import_cities --dry-run
        django-admin import_cities --dry-run --verbosity=2

    To populate the database:
        django-admin import_cities
    """

    help = "Import the content of the French cities csv file into the database."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Only print data to import")

    def handle(self, dry_run=False, **options):

        self.set_logger(options.get("verbosity"))

        with open(CITIES_JSON_FILE, "r") as raw_json_data:

            json_data = json.load(raw_json_data)
            total_len = len(json_data)
            last_progress = 0

            for i, item in enumerate(json_data):

                progress = int((100 * i) / total_len)
                if progress > last_progress + 5:
                    self.stdout.write(f"Creating cities… {progress}%")
                    last_progress = progress

                name = item["nom"]
                post_codes = item["codesPostaux"]
                code_insee = item["code"]

                department = item.get("codeDepartement")

                if not department:
                    # Sometimes department is missing. We get it from the postcode.
                    if not post_codes:
                        self.stderr.write(f"No department for {name}. Skipping…")
                        continue
                    department = department_from_postcode(post_codes[0])

                assert department in DEPARTMENTS

                coords = item.get("centre")

                # Add coords of cities for which API GEO has no data.
                if not coords and (name, code_insee) in MISSING_COORDS:
                    coords = MISSING_COORDS[(name, code_insee)]

                if coords:
                    coords = GEOSGeometry(f"{coords}")  # Feed `GEOSGeometry` with GeoJSON.
                else:
                    self.stderr.write(f"No coordinates for {name}. Skipping…")
                    continue

                slug = slugify(f"{name}-{department}")

                self.logger.debug("-" * 80)
                self.logger.debug(name)
                self.logger.debug(slug)
                self.logger.debug(post_codes)
                self.logger.debug(code_insee)
                self.logger.debug(department)
                self.logger.debug(coords)

                if not dry_run:
                    City.objects.update_or_create(
                        slug=slug,
                        defaults={
                            "department": department,
                            "name": name,
                            "post_codes": post_codes,
                            "code_insee": code_insee,
                            "coords": coords,
                        },
                    )

        self.stdout.write("-" * 80)
        self.stdout.write("Done.")
