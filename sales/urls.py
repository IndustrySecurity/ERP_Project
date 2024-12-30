from django.urls import path
from . import views

app_name = 'sales'  # 添加 app_name 声明

urlpatterns = [
     path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/details/', views.order_details, name='order_details'),  # 查看订单详情
    path('orders/<int:order_id>/edit/', views.order_edit, name='order_edit'),           # 编辑订单
    path('orders/<int:order_id>/delete/', views.order_delete, name='order_delete'),     # 删除订单
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('orders/<int:order_id>/items/', views.get_order_items, name='get_order_items'),
    path('deliveries/create/', views.delivery_create, name='delivery_create'),
    path('returns/', views.return_list, name='return_list'),
    path('orders/<int:order_id>/products/', views.get_order_products, name='get_order_products'),
    path('returns/create/', views.return_create, name='return_create'),
    ]