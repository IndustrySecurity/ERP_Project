from django import forms
from .models import CustomUser, Role
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']
        labels = {
            'username': '用户名',
            'email': '电子邮件',
            'role': '角色',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']
        labels = {
            'username': '用户名',
            'email': '电子邮件',
            'role': '角色',
            'password1': '密码',
            'password2': '确认密码',
        }
        help_texts = {
            'username': '必填。150个字符以内，仅限字母、数字和 @/./+/-/_。',
            'email': '请输入有效的电子邮件地址。',
            'role': '请选择用户的角色。',
            'password1': '密码必须至少包含8个字符，不能过于简单。',
            'password2': '请再次输入密码以确认。',
        }
        error_messages = {
            'username': {
                'required': '用户名是必填项。',
                'invalid': '请输入有效的用户名。',
            },
            'email': {
                'required': '电子邮件是必填项。',
                'invalid': '请输入有效的电子邮件地址。',
            },
            'password1': {
                'required': '密码是必填项。',
                'password_too_similar': '密码不能过于简单或与个人信息相似。',
                'password_too_common': '密码不能是常用密码。',
                'password_entirely_numeric': '密码不能完全是数字。',
            },
            'password2': {
                'required': '请确认密码。',
                'password_mismatch': '两次输入的密码不一致。',
            },
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入电子邮件'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']
        labels = {
            'name': '角色名称',
            'description': '描述',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='用户名', max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入用户名'
    }))
    password = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入密码'
    }))

    error_messages = {
        'invalid_login': "请输入正确的用户名和密码。",
        'inactive': "此账户已被禁用。",
    }