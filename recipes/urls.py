from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
]

urlpatterns += [
    path('', include('recipe.urls')),
]

urlpatterns += [
    path('', include('user.urls')),
]

urlpatterns += staticfiles_urlpatterns()

handler404 = 'recipes.views.handler404'
handler500 = 'recipes.views.handler500'
