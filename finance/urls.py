from django.urls import path
from . import views

app_name = 'finance'  

urlpatterns = [
    # 财务统计
    path('statistics/', views.finance_statistics, name='statistics'),

    # 付款记录
    path('payment_records/', views.payment_records, name='payment_records'),
    path('payment_records/view_purchase_orders',views.view_purchase_orders, name='view_purchase_orders'),
    path('payment_records/create/', views.payment_record_create, name='payment_record_create'),
    path('payment_records/delete/<int:id>/', views.delete_payment_record, name='delete_payment_record'),
    path('payment_records/view/<int:id>/', views.view_payment_record, name='view_payment_record'),
    path('payment_records/edit/<int:id>/', views.edit_payment_record, name='edit_payment_record'),

    # 收款记录
    path('receipt_records/', views.receipt_records, name='receipt_records'),
    path('receipt_records/view_sales_orders', views.view_sales_orders, name='view_sales_orders'),
    path('receipt_records/create/', views.receipt_record_create, name='receipt_record_create'),
    path('receipt_records/delete/<int:id>/', views.delete_receipt_record, name='delete_receipt_record'),
    path('receipt_records/view/<int:id>/', views.view_receipt_record, name='view_receipt_record'),
    path('receipt_records/edit/<int:id>/', views.edit_receipt_record, name='edit_receipt_record'),
]