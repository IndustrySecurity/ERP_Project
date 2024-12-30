from django.db import models
from common.base import BaseModel
from master_data.models import Material, Product

class WarehouseLocation(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name="仓库位置名称")
    description = models.TextField(blank=True, verbose_name="描述")

    def __str__(self):
        return self.name


class MaterialStock(BaseModel):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="原材料")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="仓库位置")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="库存数量")

    def __str__(self):
        return f"{self.material.name} - {self.location.name}"


class ProductStock(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="仓库位置")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="库存数量")

    def __str__(self):
        return f"{self.product.name} - {self.location.name}"


class InventoryCheck(BaseModel):
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="仓库位置")
    material_stock = models.ManyToManyField(MaterialStock, blank=True, verbose_name="原材料库存")
    product_stock = models.ManyToManyField(ProductStock, blank=True, verbose_name="产品库存")
    before_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="盘点前数量")
    after_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="盘点后数量")
    variance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="盈亏数量")
    date = models.DateField(auto_now_add=True, verbose_name="盘点日期")
    remarks = models.TextField(blank=True, verbose_name="备注")
    category = models.CharField(max_length=50, choices=[('material', '原材料'), ('product', '成品')], default='material', verbose_name="类别")
    item = models.CharField(max_length=255, verbose_name="盘点项目", blank=True)

    def __str__(self):
        return f"{self.location.name} - {self.date}"


class Transfer(BaseModel):
    from_location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, related_name="transfers_from", verbose_name="调拨自")
    to_location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, related_name="transfers_to", verbose_name="调拨到")
    category = models.CharField(max_length=20, choices=(('material', '原材料'), ('product', '产品')), verbose_name="类别")
    item = models.CharField(max_length=255, verbose_name="调拨项")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="调拨数量")
    remarks = models.TextField(blank=True, verbose_name="备注")
    date = models.DateField(auto_now_add=True, verbose_name="调拨日期")

    def __str__(self):
        return f"{self.from_location.name} -> {self.to_location.name} ({self.item})"
