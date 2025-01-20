from django import forms
from .models import Material, Product, Recipe, RecipeMaterial, Supplier, Customer, MaterialCategory, ProductCategory, ProductionLine

class MaterialForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=100, required=False, label="新类别",
        widget=forms.TextInput(attrs={'placeholder': '输入新类别（可选）'})
    )

    class Meta:
        model = Material
        fields = [
            'name', 'category', 'new_category', 'supplier', 'unit_price', 'capacity',
            'color', 'customer_supply', 'technology', 'remark'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        new_category_name = self.cleaned_data.get('new_category')
        if new_category_name:
            category, created = MaterialCategory.objects.get_or_create(name=new_category_name)
            self.instance.category = category
        return super().save(commit=commit)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'unit_price']
        labels = {
            'name': '产品名称',
            'category': '类别',
            'unit_price': '单价',
        }

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['product']
        labels = {
            'product': '产品',
        }

class RecipeMaterialForm(forms.ModelForm):
    class Meta:
        model = RecipeMaterial
        fields = ['material', 'quantity']
        labels = {
            'material': '原材料',
            'quantity': '数量',
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact', 'address']
        labels = {
            'name': '供应商名称',
            'contact': '联系方式',
            'address': '地址',
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact_info', 'email', 'address', 'grade', 'company', 'remarks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '客户名称'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '联系方式'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '电子邮件'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '地址'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '公司名称'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '备注'}),
        }

class ProductionLineForm(forms.ModelForm):
    class Meta:
        model = ProductionLine
        fields = ['name', 'description']  # 包含的字段
        labels = {
            'name': '产线名称',       # 字段标签
            'description': '描述',   # 字段标签
        }