from django.urls import path
from . import views

app_name = "production"

urlpatterns = [
    # 生产计划
    path('plans/', views.production_plan, name='production_plan'),
    path('plans/get_plans/',views.get_production_plans, name='get_production_plans'),

    # 生产工单
    path('orders/', views.production_order_list, name='production_order_list'),
    path('orders/get_products/<int:pk>/', views.get_sales_order_products, name='get_sales_order_products'),  #获取产品
    path('orders/create/', views.production_order_create, name='production_order_create'),
    path('orders/view/<int:pk>/', views.view_order, name='view_order'),
    path('orders/edit/<int:pk>/', views.production_order_edit, name='edit_order'),
    path('orders/delete/<int:pk>/', views.production_order_delete, name='production_order_delete'),

    # 领料单
    path('requisitions/', views.material_requisition_list, name='material_requisition_list'),  # 列出所有领料单
    path('requisitions/create/', views.material_requisition_create, name='material_requisition_create'),  # 创建领料单
    path('requisitions/get_materials/<int:pk>/', views.get_materials, name='get_materials'),  # 获取材料
    path('requisitions/view/<int:pk>/', views.view_requisition, name='view_material_requisition'),  # 查看领料单
    path('requisitions/delete/<int:pk>/', views.material_requisition_delete, name='delete_material_requisition'),  # 删除领料单

    # 生产入库
    path('warehousing/', views.product_warehousing_list, name='product_warehousing_list'),  # 列出入库单
    path('warehousing/create/', views.product_receipt_create, name='product_receipt_create'),  # 创建入库单
    path('warehousing/get_products/<int:pk>/', views.get_products, name='get_products'),  #获取产品
]