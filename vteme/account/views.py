from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST


from .forms import (LoginForm, ProfileEditForm, UserEditForm,
                    UserRegistrationForm)
from .models import Contact, Profile
from actions.models import Action
from actions.utils import create_action


NEW_ACCOUNT_MESSAGE = 'Создан новый аккаунт'
NUMBER_OF_ACTIONS = 10
STATUS_OK = {'status': 'ok'}
STATUS_ERROR = {'status': 'error'}
FOLLOWING_MESSAGE = 'Подписан на'

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
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related(
        'user',
        'user__profile'
    )[:NUMBER_OF_ACTIONS].prefetch_related('target')[:NUMBER_OF_ACTIONS]
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard', 'actions': actions}
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
            create_action(new_user, NEW_ACCOUNT_MESSAGE)
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


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    paginator = Paginator(users, 9)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(
        request,
        'account/user/list.html',
        {
            'section': 'people',
            'users': users
        }
    )


@login_required
def user_detail(request, username):
    user = get_object_or_404(
        User,
        username=username,
        is_active=True
    )
    return render(
        request,
        'account/user/detail.html',
        {
            'section': 'people',
            'user': user
        }
    )


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if not (user_id and action):
        return JsonResponse(STATUS_ERROR)
    try:
        user = User.objects.get(id=user_id)
        if action == 'follow':
            Contact.objects.get_or_create(
                user_from=request.user,
                user_to=user
            )
            create_action(request.user, FOLLOWING_MESSAGE, user)
        else:
            Contact.objects.filter(
                user_from=request.user,
                user_to=user
            ).delete()
        return JsonResponse(STATUS_OK)
    except User.DoesNotExist:
        return JsonResponse(STATUS_ERROR)

