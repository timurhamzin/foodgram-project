import json

from recipe.models import Ingridient

# load data to Indgridient model
if __name__ == '__main__':
    with open('ingredients.json') as f:
        ingredients = json.load(f)
    [Ingridient(title=i['title'], measurement_unit=i['dimension']).save()
     for i in ingredients]
