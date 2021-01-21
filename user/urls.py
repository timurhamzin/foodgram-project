from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),

    path('auth/', views.auth, name='auth'),
    path('signout/', views.signout, name='signout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='changePassword.html'), name='password_change'),
    path('password_change/done/', views.password_change_done,
         name='password_change_done'),

    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='resetPassword.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uuid:uidb64>/<slug:token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
