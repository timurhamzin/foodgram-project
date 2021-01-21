import json
import os

from django.core.management.base import BaseCommand, CommandError

from recipe.models import Ingridient
from recipes.settings import BASE_DIR


# load data from json to Indgridient model
class Command(BaseCommand):
    help = 'Imports ingredients to the DB'

    def handle(self, *args, **options):
        with open(os.path.join(BASE_DIR, 'ingredients.json')) as f:
            ingredients = json.load(f)
            for ingredient in ingredients:
                ingredient_obj = Ingridient(
                    title=ingredient['title'],
                    measurement_unit=ingredient['dimension'])
                ingredient_obj.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded {len(ingredients)} ingredients.'))
