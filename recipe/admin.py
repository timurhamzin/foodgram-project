from django.contrib import admin
from django.apps import apps

from recipe.models import RecipeIngridient, Recipe, Ingridient


class RecipeIngridientInline(admin.StackedInline):
    model = RecipeIngridient


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('title',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'favorite_count', 'image_tag')
    list_filter = ('author', 'title', 'tag',)
    inlines = (RecipeIngridientInline,)
    exclude = ('ingridients',)


# automatically register classes
class ListAdminMixin:
    def __init__(self, model, admin_class):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_class)


def register_models():
    models = apps.get_models()
    for model in models:
        admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
        try:
            admin.site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingridient, IngredientAdmin)
register_models()
