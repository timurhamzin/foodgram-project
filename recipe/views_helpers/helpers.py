from typing import Type

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Model
from django.forms import modelform_factory, ModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from recipe.forms import RecipeForm
from recipe.models import Recipe, RecipeIngridient, Ingridient, Tag


@login_required
def serve_shopping_list(request):
    user = request.user
    purchased_ids = list(user.purchased.values_list('recipe', flat=True))
    ingredients = {}
    purchased = Recipe.objects.filter(id__in=purchased_ids).prefetch_related(
        'recipeingridient_set', 'recipeingridient_set__ingridient')
    for recipe in purchased:
        for ri in recipe.recipeingridient_set.all():
            key = f'{ri.ingridient.title} ({ri.ingridient.measurement_unit})'
            ingredients[key] = ingredients.get(key, 0) + ri.amount
    file_data = '\n'.join(f'{k} - {v}' for k, v in ingredients.items())
    response = HttpResponse(file_data,
                            content_type='application/text charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
    return response


def get_object_or_none(model: Type[Model], **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


class RecipeEditor:

    def __init__(self, recipe, request):
        self._recipe = recipe
        self._request = request
        self.form_validation_errors = None

    def get_tags(self):
        if self._recipe.id is not None:
            return self._recipe.tag.all()
        else:
            return []

    def render_get(self, errors=None):
        all_tags = Tag.objects.all()
        ingredients = Ingridient.objects.all()
        recipe_tags = self.get_tags()
        if self._recipe.id is not None:
            recipe_ingredients = RecipeIngridient.objects.filter(
                recipe=self._recipe.id)
            form_title = 'Редактирование рецепта'
            save_title = 'Сохранить'
            edit_mode = True
        else:
            recipe_ingredients = []
            form_title = 'Создание рецепта'
            save_title = 'Создать рецепт'
            edit_mode = False
        template = 'formCreateOrEditRecipe.html'
        return render(
            self._request, template,
            {
                'recipe': self._recipe,
                'all_tags': all_tags,
                'recipe_tags': recipe_tags,
                'ingredients': ingredients,
                'recipe_ingredients': recipe_ingredients,
                'form_title': form_title,
                'save_title': save_title,
                'edit_mode': edit_mode,
                'errors': errors or {}
            },
        )

    def update_recipe_image(self):
        if 'file' in self._request.FILES.keys():
            image = self._request.FILES['file']
            self._recipe.image.save(
                default_storage.get_available_name(image.name), image)

    def validate_recipe_with_form(self) -> ModelForm:
        self.form_validation_errors = None
        data = self.get_recipe_data()
        Form = modelform_factory(Recipe, form=RecipeForm, fields=data.keys())
        form = Form(data, instance=self._recipe)
        if form.is_valid():
            return form
        else:
            self.form_validation_errors = {
                v: form.errors[k] for k, v in
                self.model_fields_to_input_names.items() if k in form.errors
            }

    @property
    def model_fields_to_input_names(self):
        return {'description': 'discription', 'title': 'name',
                'cooking_time': 'cooking_time'}

    def get_recipe_data(self):
        raw_data = self._request.POST.dict()
        result = {k: raw_data[v] for k, v in
                  self.model_fields_to_input_names.items()}
        return result

    def create_recipe_tags(self):
        raw_data = self._request.POST.dict()
        all_tags = Tag.objects.all()
        tags_to_set = [k for k in raw_data.keys()
                       if k in list(all_tags.values_list('name', flat=True))]
        present_tags = self._recipe.tag.all()
        present_tags_set = set(present_tags.values_list('name', flat=True))
        tags_to_set_set = set(tags_to_set)
        if present_tags_set != tags_to_set_set:
            remove_tags = present_tags_set - tags_to_set_set
            add_tags = tags_to_set_set - present_tags_set
            if remove_tags:
                self._recipe.tag.remove(*list(
                    all_tags.filter(
                        name__in=remove_tags).values_list('id', flat=True)))
            if add_tags:
                self._recipe.tag.add(
                    *all_tags.filter(
                        name__in=add_tags).values_list('id', flat=True))
        self._recipe.save()

    def create_recipe_ingredients(self):
        raw_data = self._request.POST.dict()
        RecipeIngridient.objects.filter(recipe__id=self._recipe.id).delete()
        ingredient_titles = [raw_data[k] for k in raw_data.keys()
                             if k.startswith('nameIngredient')]
        amounts = [raw_data[k] for k in raw_data.keys()
                   if k.startswith('valueIngredient')]
        for ingredient_title, amount in zip(ingredient_titles, amounts):
            ingredient = get_object_or_404(Ingridient, title=ingredient_title)
            RecipeIngridient.objects.create(recipe=self._recipe,
                                            ingridient=ingredient,
                                            amount=amount)
