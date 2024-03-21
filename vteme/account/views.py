from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .forms import (LoginForm, ProfileEditForm, UserEditForm,
                    UserRegistrationForm)
from .models import Profile


def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            return HttpResponse('Invalid login')
        data = form.cleaned_data
        user = authenticate(
            request,
            username=data['username'],
            password=data['password']
        )
        if user is None:
            return HttpResponse('Invalid credentials')
        if not user.is_active:
            return HttpResponse('Disabled account')
        login(request, user)
        return HttpResponse('Authenticated successfully')
    return render(
        request,
        'account/login.html',
        {'form': form}
    )


@login_required
def dashboard(request):
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard'}
    )


def register(request):
    user_form = UserRegistrationForm()
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(
                request,
                'account/register_done.html',
                {'new_user': new_user}
            )
    return render(
        request,
        'account/register.html',
        {'user_form': user_form}
    )


@login_required
def edit(request):
    user_form = UserEditForm(instance=request.user)
    profile_form = ProfileEditForm(instance=request.user.profile)
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен.')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
    return render(
        request,
        'account/edit.html',
        {'user_form': user_form,
         'profile_form': profile_form}
    )
