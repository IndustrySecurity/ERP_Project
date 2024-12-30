from django import forms
from .models import MaterialStock, ProductStock, InventoryCheck, WarehouseLocation, Transfer


class MaterialStockForm(forms.ModelForm):
    class Meta:
        model = MaterialStock
        fields = ['material', 'location', 'quantity']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ['product', 'location', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class InventoryCheckForm(forms.ModelForm):
    class Meta:
        model = InventoryCheck
        fields = ['location', 'category', 'item', 'after_quantity', 'remarks']

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['from_location', 'to_location', 'category', 'item', 'quantity', 'remarks']
