from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('', views.role_list, name='role_list'),
    path('create/', views.role_create, name='role_create'),
    path('update/<int:pk>/', views.role_update, name='role_update'),
    path('delete/<int:pk>/', views.role_delete, name='role_delete'),
]
