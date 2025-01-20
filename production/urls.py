from django.urls import path
from . import views

app_name = "production"

urlpatterns = [

    # 生产工单
    path('orders/', views.production_order_list, name='production_order_list'),
    path('orders/create/', views.production_order_create, name='production_order_create'),
    path('orders/view/<int:pk>/', views.view_order, name='view_order'),
    path('orders/edit/<int:pk>/', views.production_order_edit, name='edit_order'),
    path('orders/delete/<int:pk>/', views.production_order_delete, name='production_order_delete'),

    # 领料单
    path('requisitions/', views.material_requisition_list, name='material_requisition_list'),  # 列出所有领料单
    path('requisitions/create/', views.material_requisition_create, name='material_requisition_create'),  # 创建领料单
    path('requisitions/get_materials/<int:pk>/', views.get_materials, name='get_materials'),  # 获取材料
    #path('requisitions/view/<int:pk>/', views.view_requisition, name='view_material_requisition'),  # 查看领料单
    #path('requisitions/edit/<int:pk>/', views.material_requisition_edit, name='edit_material_requisition'),  # 编辑领料单
    #path('requisitions/delete/<int:pk>/', views.material_requisition_delete, name='delete_material_requisition'),  # 删除领料单

]