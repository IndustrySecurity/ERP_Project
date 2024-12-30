from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('locations/', views.warehouse_location_list, name='warehouse_location_list'),
    path('locations/create/', views.warehouse_location_create, name='warehouse_location_create'),
    path('material_stock/', views.material_stock_list, name='material_stock_list'),
    path('material_stock/create/', views.material_stock_create, name='material_stock_create'),
    path('material_stock/delete/<int:pk>/', views.material_stock_delete, name='material_stock_delete'),
    path('material_stock/edit/<int:pk>/', views.material_stock_edit, name='material_stock_edit'),
    path('product_stock/', views.product_stock_list, name='product_stock_list'),
    path('product_stock/create/', views.product_stock_create, name='product_stock_create'),
    path('product_stock/delete/<int:pk>/', views.product_stock_delete, name='product_stock_delete'),
    path('product_stock/edit/<int:pk>/', views.product_stock_edit, name='product_stock_edit'),
    path('inventory_checks/', views.inventory_check_list, name='inventory_check_list'),
    path('inventory_checks/create/', views.inventory_check_create, name='inventory_check_create'),
    path('transfer/', views.inventory_transfer_create, name='inventory_transfer_create'),
    path('get_items/', views.get_items, name='get_items'),  # 新增
    path('get_quantity/', views.get_quantity, name='get_quantity'),  # 新增
    path('stock/<int:location_id>/<int:product_id>/', views.get_stock_quantity, name='get_stock_quantity'),
]
