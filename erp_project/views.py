from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import CustomAuthenticationForm  # Import the custom form

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # 登录成功后重定向到主页
            else:
                # 用户名或密码错误
                form.add_error(None, '用户名或密码错误')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'home.html')