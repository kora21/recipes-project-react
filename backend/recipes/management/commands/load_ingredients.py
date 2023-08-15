import csv

from django.core.management import BaseCommand
from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

MODELS_DATA = {
    Ingredient: 'ingredients.csv'
}

CSV_PATH = f'{BASE_DIR}/data/'


class Command(BaseCommand):

    def handle(self, *args, **options):
        for model, csv_file in MODELS_DATA.items():
            with open(str(CSV_PATH) + csv_file, mode="r", encoding="utf-8"
                      ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    model.objects.get_or_create(**row)
            self.stdout.write(self.style.SUCCESS(
                'Данные загружены.'
            ))
