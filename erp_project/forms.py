from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='用户名', max_length=254)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)