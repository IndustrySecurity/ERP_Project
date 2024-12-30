from django.urls import path
from . import views

app_name = "purchase"

urlpatterns = [
    # Purchase Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/create/", views.order_create, name="order_create"),
    path("orders/view/<int:pk>/", views.order_view, name="order_view"),
    path("orders/edit/<int:pk>/", views.order_edit, name="order_edit"),
    path("orders/delete/<int:pk>/", views.order_delete, name="order_delete"),

    
    # Purchase Receipts
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/create/', views.receipt_create, name='receipt_create'),
    path('orders/<int:order_id>/items/', views.get_order_items, name='get_order_items'),
    path('orders/<int:order_id>/materials/', views.get_order_materials, name='get_order_materials'),
    
    # Purchase Returns
    path("returns/", views.return_list, name="return_list"),
    path("returns/create/", views.return_create, name="return_create"),
    path("returns/delete/<int:pk>/", views.return_delete, name="return_delete"),
    path('materials/stock/', views.get_material_stock, name='get_material_stock')
]
