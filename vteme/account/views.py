from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login

from .forms import LoginForm


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
            return HttpResponse('Diabled account')
        login(request, user)
        return HttpResponse('Authenticated successfuly')
    return render(
        request,
        'account/login.html',
        {'form': form}
    )
