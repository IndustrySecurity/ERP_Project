from django.db import models
from common.base import BaseModel
from warehouse.models import WarehouseLocation
from master_data.models import Material, Supplier

class PurchaseOrder(BaseModel):
    order_number = models.CharField(max_length=255, unique=True, verbose_name="订单编号")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="供应商")
    materials = models.ManyToManyField(Material, through='PurchaseOrderItem', verbose_name="采购物料")
    status = models.CharField(
        max_length=50,
        choices=(('pending', '待处理'), ('received', '已入库'), ('returned', '已退货')),
        default='pending',
        verbose_name="订单状态"
    )
    def total_price(self):
        """计算总价"""
        return sum(item.unit_price * item.quantity for item in self.purchaseorderitem_set.all())

    def save(self, *args, **kwargs):
        # 确保 order_number 唯一
        if not self.pk and not self.order_number:  # 仅在新建时生成
            prefix = "PO"
            # 查询最新的订单编号后递增
            last_order = PurchaseOrder.objects.order_by('-id').first()
            next_id = (last_order.id + 1) if last_order else 1
            self.order_number = f"{prefix}-{next_id:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class PurchaseOrderItem(BaseModel):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, verbose_name="采购订单")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="物料")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")

    def __str__(self):
        return f"{self.material.name} - {self.order.order_number}"


class PurchaseReceipt(BaseModel):
    receipt_number = models.CharField(max_length=255, unique=True, verbose_name="入库单编号")
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, verbose_name="采购订单")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="仓库位置")
    date = models.DateField(auto_now_add=True, verbose_name="入库日期")
    remarks = models.TextField(blank=True, verbose_name="备注")

    def __str__(self):
        return self.receipt_number


class PurchaseReturn(BaseModel):
    return_number = models.CharField(max_length=255, unique=True, verbose_name="退库单编号")
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, verbose_name="采购订单")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="退货物料")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="退货数量")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="退货仓库")
    date = models.DateField(auto_now_add=True, verbose_name="退货日期")
    remarks = models.TextField(blank=True, verbose_name="备注")

    def __str__(self):
        return self.return_number
