from django.db import models
from common.base import BaseModel  # 确保 BaseModel 已定义
from django.utils.timezone import now


class Supplier(BaseModel):
    name = models.CharField(max_length=255, verbose_name="供应商名称")
    contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="联系方式")
    address = models.TextField(blank=True, null=True, verbose_name="地址")

    def __str__(self):
        return self.name


from django.db import models
from common.base import BaseModel


class Customer(BaseModel):
    CUSTOMER_GRADES = (
        ('A', '一级客户'),
        ('B', '二级客户'),
        ('C', '三级客户'),
    )

    name = models.CharField(max_length=255, unique=True, verbose_name="客户名称")
    contact_info = models.CharField(max_length=255, blank=True, verbose_name="联系方式")
    email = models.EmailField(blank=True, verbose_name="电子邮件")
    address = models.TextField(blank=True, verbose_name="地址")
    grade = models.CharField(
        max_length=1, choices=CUSTOMER_GRADES, default='C', verbose_name="客户等级"
    )
    company = models.CharField(max_length=255, blank=True, verbose_name="公司名称")
    remarks = models.TextField(blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.name



class MaterialCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="原材料类别")

    def __str__(self):
        return self.name

    @staticmethod
    def get_default_category():
        # 确保返回主键值，而不是实例
        category, _ = MaterialCategory.objects.get_or_create(name="无")
        return category.id  # 返回主键值



class ProductCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="产品类别")

    def __str__(self):
        return self.name


class Material(BaseModel):
    material_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name="料号")
    name = models.CharField(max_length=255, verbose_name="原材料名称")
    category = models.ForeignKey(
        MaterialCategory, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="类别", default=MaterialCategory.get_default_category
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="供应商")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    capacity = models.CharField(max_length=50, blank=True, null=True, verbose_name="容量")
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="颜色")
    customer_supply = models.CharField(
        max_length=10,
        choices=[('客供', '客供'), ('非客供', '非客供')],
        default='非客供',
        verbose_name="客供/非客供"
    )
    technology = models.TextField(blank=True, null=True, verbose_name="工艺技术")
    remark = models.TextField(blank=True, null=True, verbose_name="备注")

    def save(self, *args, **kwargs):
            is_new = self.pk is None  # 判断是否是新记录
            super().save(*args, **kwargs)  # 先保存以生成 pk
            if is_new and not self.material_number:  # 仅在新建时生成料号
                prefix = "MAT"
                date_str = now().strftime('%Y%m%d')
                self.material_number = f"{prefix}-{date_str}-{self.pk:06d}"
                super().save(update_fields=['material_number'])  # 更新料号字i段

    def __str__(self):
        return self.name



class Product(BaseModel):
    product_code = models.CharField(max_length=20, unique=True, verbose_name="产品编号")
    name = models.CharField(max_length=255, verbose_name="产品名称")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="类别")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    material = models.CharField(max_length=255, null=True, blank=True, verbose_name="容器材质")
    capacity = models.CharField(max_length=50, null=True, blank=True, verbose_name="容量")
    technology = models.TextField(null=True, blank=True, verbose_name="工艺技术")
    color = models.CharField(max_length=50, null=True, blank=True, verbose_name="颜色")
    contract_date = models.DateField(null=True, blank=True, verbose_name="合同日期")
    remark = models.TextField(null=True, blank=True, verbose_name="备注")

    def save(self, *args, **kwargs):
        if not self.product_code:
            prefix = "PRD"
            last_product = Product.objects.order_by("-id").first()
            last_number = int(last_product.product_code.split("-")[-1]) if last_product else 0
            self.product_code = f"{prefix}-{last_number + 1:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Recipe(BaseModel):
    recipe_number =  models.CharField(max_length=255, unique=True, verbose_name="配方编号")
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="产品")
    materials = models.ManyToManyField(Material, through='RecipeMaterial', verbose_name="原材料")
    description = models.TextField(blank=True, null=True, verbose_name="描述")  # 添加描述字段

    def __str__(self):
        return f"{self.product.name} 配方"

    def total_material_quantity(self):
        return sum([rm.quantity for rm in self.recipematerial_set.all()])
    
    def save(self, *args, **kwargs):
        # 确保 recipe_number 唯一
        if not self.pk and not self.recipe_number:  # 仅在新建时生成
            prefix = "RP"
            # 查询最新的订单编号后递增
            last_recipe = Recipe.objects.order_by('-id').first()
            next_id = (last_recipe.id + 1) if last_recipe else 1
            self.recipe_number = f"{prefix}-{next_id:06d}"
        super().save(*args, **kwargs)


class RecipeMaterial(BaseModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="配方")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="原材料")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")

    def __str__(self):
        return f"{self.material.name} in {self.recipe.product.name}"
    

class ProductionLine(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="产线名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")

    def __str__(self):
        return self.name
