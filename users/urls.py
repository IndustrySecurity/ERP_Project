from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('list/', views.user_list_ajax, name='user_list_ajax'),  # 新增路由
    path('create/',  views.user_create, name='user_create'),
    path('edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('delete/<int:pk>/', views.user_delete, name='user_delete'),
    path('roles/', views.role_list, name='role_list'),
    path('roles/list/', views.role_list_ajax, name='role_list_ajax'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/edit/<int:pk>/', views.role_edit, name='role_edit'),
    path('roles/delete/<int:pk>/', views.role_delete, name='role_delete'),
]
