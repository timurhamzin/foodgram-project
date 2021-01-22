import json
import os

from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand, CommandError

from recipe.models import Ingridient
from recipes.settings import BASE_DIR


# load data from json to Indgridient model
class Command(BaseCommand):
    help = 'Imports ingredients and tags to the DB'

    def load_ingredients(self):
        with open(os.path.join(BASE_DIR, 'fixtures', 'ingredients.json')) as f:
            ingredients = json.load(f)
            for ingredient in ingredients:
                ingredient_obj, created = Ingridient.objects.get_or_create(
                    title=ingredient['title'],
                    measurement_unit=ingredient['dimension'])
                if created:
                    msg = f'Successfully loaded {len(ingredients)} ingredients.'
                    self.stdout.write(self.style.SUCCESS(msg))

    @staticmethod
    def load_tags():
        execute_from_command_line(
            ["manage.py", "loaddata", "fixtures/tag.json"])

    def handle(self, *args, **options):
        self.load_ingredients()
        self.load_tags()
