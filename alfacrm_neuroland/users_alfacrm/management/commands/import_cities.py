import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from users_alfacrm.models import City, Coordinaties


def get_json_data(file_name: str):
    json_path = os.path.join(settings.BASE_DIR, "static/data/", file_name)
    with open(json_path, "r") as json_file:
        return json.load(json_file)


class Command(BaseCommand):
    def handle(self, *args, **options):
        json_data = get_json_data("ru_cities.json")
        for item in json_data:
            coords = item["coords"]
            coordinaties = Coordinaties.objects.create(
                lat=coords["lat"], lon=coords["lon"]
            )
            City.objects.create(
                coordinaties=coordinaties,
                district=item["district"],
                name=item["name"],
                population=item["population"],
                subject=item["subject"],
            )
        print("cities - OK")
