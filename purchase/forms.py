from django import forms
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, PurchaseReturn

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'status', 'remarks']

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['material', 'quantity', 'unit_price']

class PurchaseReceiptForm(forms.ModelForm):
    class Meta:
        model = PurchaseReceipt
        fields = ['order', 'receipt_date', 'warehouse_location', 'remarks']

class PurchaseReturnForm(forms.ModelForm):
    class Meta:
        model = PurchaseReturn
        fields = ['order', 'return_date', 'remarks']
