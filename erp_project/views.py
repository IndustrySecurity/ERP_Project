from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import CustomAuthenticationForm  # Import the custom form
from django.contrib.auth.decorators import login_required
from master_data.models import Material, Product, Supplier, Customer

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

@login_required
def home(request):
    # 获取各种类型的数据计数
    materials_count = Material.objects.count()
    products_count = Product.objects.count()
    suppliers_count = Supplier.objects.count()
    customers_count = Customer.objects.count()
    
    context = {
        'materials_count': materials_count,
        'products_count': products_count,
        'suppliers_count': suppliers_count,
        'customers_count': customers_count,
    }
    return render(request, 'home.html', context)

def login_redirect(request):
    return redirect('login')