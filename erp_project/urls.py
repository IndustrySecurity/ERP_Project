from django.contrib import admin
from django.urls import include, path
from .views import login_view, home_view, logout_view
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('roles/', include('roles.urls')),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('master_data/', include('master_data.urls', namespace='master_data')),  # 确保 namespace 存在
    path('purchase/', include('purchase.urls', namespace='purchase')),
    path('sales/', include('sales.urls', namespace='sales')),
    path('production/', include('production.urls', namespace='production')),
    path('warehouse/', include('warehouse.urls', namespace='warehouse')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('home/', login_required(home_view), name='home'),
    path('', lambda request: redirect('login')),
]