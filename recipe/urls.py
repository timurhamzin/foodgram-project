from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('favorite_list/', views.favorite_list, name='favorite_list'),
    path('<int:recipe_id>/', views.single_page, name='single_page'),
    path('create/', views.create_recipe, name='create_recipe'),
    path('<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),
    path('purchases/', views.ShoppingCartView.as_view()),
    path('purchases/<int:followed_id>/', views.ShoppingCartView.as_view()),
    path('subscriptions/', views.FollowUserView.as_view()),
    path('subscriptions/<int:followed_id>/', views.FollowUserView.as_view()),
    path('my_followed/', views.my_followed, name='my_followed'),
    path('author/<int:author_id>/', views.author, name='author'),
    path('favorites/', views.FollowRecipeView.as_view()),
    path('favorites/<int:followed_id>/', views.FollowRecipeView.as_view()),
    path('about/', views.FlatPageAbout.as_view(), name='about'),
    path('technology/', views.FlatPageTechnology.as_view(), name='technology'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
