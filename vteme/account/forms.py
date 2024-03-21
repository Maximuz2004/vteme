from django import forms
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']

    def clean_email(self):
        user_email = self.cleaned_data['email']
        if User.objects.filter(email=user_email).exists():
            raise forms.ValidationError(
                'Пользователь с такой почтой уже существует'
            )
        return user_email


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        user_email = self.cleaned_data['email']
        filtered_users = User.objects.exclude(
            id=self.instance.id
        ).filter(email=user_email)
        if filtered_users.exists():
            raise forms.ValidationError('Такой email уже используется')
        return user_email



class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']
