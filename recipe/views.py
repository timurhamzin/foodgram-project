import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from recipe.models import (Recipe, Tag, FollowRecipe, ShoppingCart, FollowUser)
from recipe.templatetags.user_title import user_title
from recipe.views_helpers.helpers import (
    serve_shopping_list, get_object_or_none, RecipeEditor)

User = get_user_model()

CARDS_PER_PAGE = 6
FOLLOWED_PER_PAGE = 6
DEFAULT_TAG_VALUE = 1


class FlatPageAbout(TemplateView):
    template_name = 'flatpages/title_and_text.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Об авторе сайта'
        context['text'] = '''
            Меня зовут Тимур Хамзин.<br>
            Я Python-программист.<br>
            С этим и другими моими проектами вы можете ознакомиться
            <a href="https://github.com/timurhamzin">здесь</a>.<br>
        '''
        return context


class FlatPageTechnology(TemplateView):
    template_name = 'flatpages/title_and_text.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О технологиях'
        context['text'] = '''
            Для создания этого сайта использовались следующии технологии:<br>
            <br>
            Python<br>
            Django<br>
            БД PostgreSQL<br>
            Docker<br>
            Docker-compose<br>
            Docker Hub<br>
            Gunicorn<br>
            Nginx<br>
            Github Actions<br>
            Ubuntu<br>
            <br>
            <a href="https://github.com/timurhamzin/foodgram-project">
                Подробнее
            </a><br>
        '''
        return context


def index(request, only_favorite=False, by_author=None):
    # set context variables
    user = request.user
    get_dict = request.GET.dict()
    all_tags = Tag.objects.all()  # need both names and colors of all tags
    selected_tags = [t.name for t in all_tags
                     if get_dict.get(t.name, str(DEFAULT_TAG_VALUE)) == '1']

    # select recipes
    recipes = Recipe.objects.filter(
        Q(tag__name__in=selected_tags) | Q(tag=None))
    title = 'Рецепты'
    if request.user.is_authenticated:
        followed = list(user.follow_recipes.values_list('recipe', flat=True))
        purchased_recipes = list(
            user.purchased_recipes.values_list('id', flat=True))
        if only_favorite:
            title = f'Избранные рецепты'
            recipes = recipes.filter(id__in=followed)
    else:
        followed = None
        purchased_recipes = None

    if by_author is not None:
        selected_author = get_object_or_404(User, id=by_author)
        title = user_title(selected_author)
        recipes = recipes.filter(author=by_author)

    recipes = recipes.order_by('-pub_date').distinct()

    # set pages
    paginator = Paginator(recipes, CARDS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    return render(
        request, 'indexAuth.html',
        {
            'page': page,
            'paginator': paginator,
            'recipes': recipes,
            'all_tags': all_tags,
            'tag_filters': {},
            'shopping_cart': {},
            'purchased': purchased_recipes,
            'favorites': followed,
            'page_title': title,
            'by_author': by_author,
        },
    )


def favorite_list(request):
    return index(request, only_favorite=True)


@login_required
def my_followed(request):
    user = request.user
    author_ids = list(user.follows.values_list('author', flat=True))
    authors = User.objects.filter(id__in=author_ids)
    paginator = Paginator(authors, FOLLOWED_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    return render(
        request, 'myFollow.html',
        {
            'page': page,
            'paginator': paginator,
            'authors': authors
        },
    )


@login_required
def shopping_cart(request):
    user = request.user
    download = request.GET.get('download')
    if download:
        return serve_shopping_list(request)
    else:
        recipe_ids = list(user.purchased.values_list('recipe', flat=True))
        recipes = Recipe.objects.filter(id__in=recipe_ids)
        return render(
            request, 'shopList.html',
            {
                'recipes': recipes
            },
        )


def author(request, author_id):
    return index(request, by_author=author_id)


def single_page(request, recipe_id):
    recipe = get_object_or_404(Recipe.objects.prefetch_related(
        Prefetch('recipeingridient_set', to_attr='recipe_ingredients')),
        id=recipe_id)
    return render(
        request, 'singlePage.html',
        {
            'recipe': recipe,
            'tags': recipe.tag.all(),
            'recipe_ingredients': recipe.recipe_ingredients,
            'favorite': FollowRecipeView.is_followed(recipe, request.user),
            'in_cart': ShoppingCartView.is_followed(recipe, request.user),
            'subscribed': FollowUserView.is_followed(
                recipe.author, request.user)
        },
    )


class FollowThrough(View, LoginRequiredMixin):
    # override class attributes in child classes
    _followed_through_name = ''
    _followed_class = None
    _through_class = None
    _follow_counter_field_name = ''

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        result = JsonResponse({'success': False})
        request_body = json.loads(request.body)
        followed_id = request_body.get('id')
        if followed_id is not None:
            followed_obj = get_object_or_404(
                self._followed_class, id=followed_id)
            filter_kwargs = {self._followed_through_name: followed_obj}
            through_obj, created = self._through_class.objects.get_or_create(
                user=request.user, **filter_kwargs)
            if created:
                result = JsonResponse({'success': True})
            self.update_counter(followed_obj, 1)
        else:
            result = JsonResponse({'success': False}, 400)
        return result

    def delete(self, request, followed_id):
        filter_kwargs = {self._followed_through_name: followed_id}
        try:
            through_obj = get_object_or_404(
                self._through_class.objects.select_related(
                    self._followed_through_name),
                user=request.user, **filter_kwargs
            )
            followed_obj = getattr(through_obj, self._followed_through_name)
            through_obj.delete()
            self.update_counter(followed_obj, -1)
        except Http404:
            pass
        return JsonResponse({'success': True})

    @classmethod
    def is_followed(cls, followed, user):
        if user.is_authenticated:
            filter_kwargs = {cls._followed_through_name: followed}
            found = get_object_or_none(cls._through_class,
                                       user=user, **filter_kwargs)
            return found is not None
        else:
            return False

    def update_counter(self, followed_obj, add):
        if self._follow_counter_field_name:
            count = getattr(followed_obj, self._follow_counter_field_name)
            setattr(followed_obj, self._follow_counter_field_name, count + add)
            followed_obj.save()


class FollowRecipeView(FollowThrough):
    _followed_through_name = 'recipe'
    _followed_class = Recipe
    _through_class = FollowRecipe
    _follow_counter_field_name = 'favorite_count'


class FollowUserView(FollowThrough):
    _followed_through_name = 'author'
    _followed_class = User
    _through_class = FollowUser


class ShoppingCartView(FollowThrough):
    _followed_through_name = 'recipe'
    _followed_class = Recipe
    _through_class = ShoppingCart


@login_required
def edit_recipe(request, recipe_id):
    if recipe_id is not None:
        recipe = get_object_or_404(Recipe, id=recipe_id)
    else:
        recipe = Recipe(author=request.user)
    editor = RecipeEditor(recipe, request)
    if recipe.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'GET':
        return editor.render_get()
    elif request.method == 'POST':
        form = editor.validate_recipe_with_form()
        if form:
            form.save()
            editor.update_recipe_image()
            editor.create_recipe_tags()
            editor.create_recipe_ingredients()
            return redirect(
                reverse('single_page', kwargs=dict(recipe_id=recipe.id)))
        else:
            return editor.render_get(errors=editor.form_validation_errors)


@login_required
def create_recipe(request):
    return edit_recipe(request, None)


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponseForbidden()
    recipe.delete()
    return redirect(reverse('index'))
