from django.urls import path
from . import views

app_name = 'master_data'  # 定义命名空间

urlpatterns = [
    # 原材料
    path('materials/', views.material_list, name='material_list'),
    path("materials/list/", views.material_list_ajax, name="material_list_ajax"),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/edit/<int:pk>/', views.material_edit, name='material_edit'),
    path('materials/delete/<int:pk>/', views.material_delete, name='material_delete'),

    # 产品
    path('products/', views.product_list, name='product_list'),
    path('products/list/', views.product_list_ajax, name='product_list_ajax'),
    path('products/create/', views.product_create_ajax, name='product_create_ajax'),
    path('products/edit/<int:pk>/', views.product_edit_ajax, name='product_edit_ajax'),
    path('products/delete/<int:pk>/', views.product_delete_ajax, name='product_delete_ajax'),

    # 配方
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/create/', views.recipe_create, name='recipe_create'),
    path('recipes/update/<int:pk>/', views.recipe_update, name='recipe_update'),
    path('recipes/delete/<int:pk>/', views.recipe_delete, name='recipe_delete'),

    # 供应商
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/list/', views.supplier_list_ajax, name='supplier_list_ajax'),
    path('suppliers/create/', views.supplier_create_ajax, name='supplier_create'),
    path('suppliers/edit/<int:pk>/', views.supplier_edit_ajax, name='supplier_edit'),
    path('suppliers/delete/<int:pk>/', views.supplier_delete_ajax, name='supplier_delete'),

    # 客户
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
]
