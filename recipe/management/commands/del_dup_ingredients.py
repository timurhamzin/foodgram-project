from django.db.models import Min, Count
import json
import os

from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand, CommandError

from recipe.models import Ingridient
from recipes.settings import BASE_DIR


# load data from json to Indgridient model
class Command(BaseCommand):
    help = 'Imports ingredients and tags to the DB'

    def handle(self, *args, **options):
        master_pks = Ingridient.objects.values(
            'title', 'measurement_unit').annotate(
            Min('pk'), count=Count('pk')).filter(
            count__gt=1).values_list(
            'pk__min', flat=True)
        masters = Ingridient.objects.in_bulk(list(master_pks))

        for master in masters.values():
            duplicates = Ingridient.objects.filter(
                title=master.title, measurement_unit=master.measurement_unit
            ).exclude(pk=master.pk)
            if duplicates:
                duplicates.delete()
