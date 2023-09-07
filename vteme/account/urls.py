from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'account'

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy('account:password_change_done'),
            template_name='registration/password_change_form.html'
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy('account:password_reset_done'),
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy('account:password_reset_complete'),
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password_reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path('', views.dashboard, name='dashboard')
]
