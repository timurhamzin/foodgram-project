from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.safestring import mark_safe

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор')
    title = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipe_images', blank=True, null=True,
        verbose_name='Внешний вид')
    description = models.TextField(verbose_name='Описание')
    ingridients = models.ManyToManyField(
        'Ingridient', through='RecipeIngridient', related_name='recipes',
        verbose_name='Ингридиенты'
    )
    tag = models.ManyToManyField('Tag', blank=False, verbose_name='Тэг')
    cooking_time = models.PositiveSmallIntegerField(
        null=False, blank=True, default=0, verbose_name='Время приготовления')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')
    purchased_by = models.ManyToManyField(
        User, blank=True, related_name='purchased_recipes',
        through='ShoppingCart', verbose_name='Покупатели')
    favorite_count = models.PositiveIntegerField(
        default=0, verbose_name='Добавлено в избранное (раз)')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def image_tag(self):
        return mark_safe(f'<img src="{settings.MEDIA_URL}'
                         f'{self.image}" height="30"/>')

    image_tag.short_description = 'Image'


class Ingridient(models.Model):
    title = models.CharField(
        max_length=200, verbose_name='Название', null=False, blank=False)
    measurement_unit = models.CharField(
        max_length=20, verbose_name='Единица измерения', null=False, blank=False
    )
    part = models.ManyToManyField(Recipe, through='RecipeIngridient')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'measurement_unit'],
                                    name='title_n_unit_ingredient_unique')
        ]
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.title


class RecipeIngridient(models.Model):
    ingridient = models.ForeignKey(
        Ingridient, on_delete=models.CASCADE, related_name='recipe_ingridients',
        verbose_name='Ингридиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингридиент рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'


class Tag(models.Model):
    name = models.CharField(max_length=10, verbose_name='Имя тэга')
    ORANGE = 'orange'
    GREEN = 'green'
    PURPLE = 'purple'
    COLOR_CHOICES = [
        (ORANGE, 'orange'),
        (GREEN, 'green'),
        (PURPLE, 'purple'),
    ]

    badge_color = models.CharField(
        max_length=32, choices=COLOR_CHOICES, default=ORANGE,
        verbose_name='Цвет ярлыка'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class FollowRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follow_recipes',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='follow_recipes',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='user_n_recipe_fav_unique')
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'User {self.user} follows recipe {self.recipe}'


class FollowUser(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follows',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followed_by',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='user_n_author_follow_unique')
        ]

    def __str__(self):
        return f'User {self.user} follows author {self.author}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='purchased',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='user_n_recipe_cart_unique')
        ]

    def __str__(self):
        return f'User {self.user} added {self.recipe} to their shopping cart'
